import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from scrapy.utils.response import open_in_browser

from product_spiders.items import Product, ProductLoader

import logging


#user_agent = 'Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1'
user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5'


class AmazonComSpider(BaseSpider):
    name = 'amazon.com_espresso'
    allowed_domains = ['amazon.com']

    start_urls = ('http://www.amazon.com', )

    headers = {
        'User-agent': user_agent
    }
    form_headers = {
        'User-agent': user_agent,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    category_ids = [
        '2251595011',
        '2251593011',
        '2251592011',
        '915194'
    ]

    search_url = "http://www.amazon.com/s/ref=nb_sb_noss?keywords=espresso&node=%%cat_id%%"

    def start_requests(self):
        for cat_id in self.category_ids:
            yield Request(
                self.search_url.replace("%%cat_id%%", cat_id),
                headers=self.headers,
                callback=self.parse
                )
    def parse(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        total = hxs.select("//h2[@id='resultCount']//text()").re("Showing .*? - .*? of (.*?) Results")
        bottom = hxs.select("//h2[@id='resultCount']//text()").re("Showing (.*?) - .*? of .*? Results")
        top = hxs.select("//h2[@id='resultCount']//text()").re("Showing .*? - (.*?) of .*? Results")
        if total:
            total = int(total[0].replace(",", ""))
            logging.error("Total: %d" % total)
        if top and bottom:
            top = int(top[0].replace(",", ""))
            bottom = int(bottom[0].replace(",", ""))
        else:
            logging.error("No numbers!")
            logging.error("Top: %s" % top)
            logging.error("Bottom: %s" % bottom)
            return

        # parse products
        items = hxs.select("//div[contains(@class, 'result') and contains(@class, 'product')]")
        if not items:
            logging.error("ERROR! No products %s" % response.url)
            if top - bottom > 0:
                logging.error("Products exist but not found!")

        items_count = 0
        counter = 0
        for item in items:
            counter += 1
            name = item.select("div[@class='data']/h3/a/text()").extract()
            if not name:
                name = item.select("div[@class='data']/h3/a/span/@title").extract()
                if not name:
                    logging.error("ERROR! NO NAME! URL: %s" % response.url)
                    continue
            name = name[0]
            logging.error("%d. Name: %s" % (counter, name))

            url = item.select("div[@class='data']/h3/a/@href").extract()
            if not url:
                logging.error("ERROR! NO URL! URL: %s. NAME: %s" % (response.url, name))
                continue
            url = url[0]
            url = urljoin_rfc(URL_BASE, url)
            logging.error("%d. URL: %s" % (counter, url))
            price = item.select("div/div[contains(@class,'newPrice')]/span[contains(@class, 'price')]/text()").extract()
            if not price:
                price = item.select("div/div[@class='usedNewPrice']/span[@class='subPrice']/span[@class='price']/text()").extract()
                if not price:
                    external = hxs.select(".//div[@class='prodAds']")
                    if external:
                        logging.error("External site")
                    else:
                        logging.error("ERROR! No price! URL: %s. NAME: %s" % (response.url, name))
                    continue
            price = price[0]
            logging.error("%d. Price: %s" % (counter, price))

            l = ProductLoader(item=Product(), response=response)
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()
            items_count += 1

        logging.error("Found %d items" % len(items))
        logging.error("Processed %d items" % items_count)

        # get current page number
        m = re.search("page=([\d]*)&", response.url)
        if not m:
            current_page_number = 0
        else:
            current_page_number = int(m.group(1))

        # pages
        pages = hxs.select("//span[@class='pagnLink']/a/@href").extract()
        for url in pages:
            m = re.search("page=([\d]*)&", url)
            if not m:
                continue
            else:
                page_number = int(m.group(1))
            if page_number > current_page_number:
                request = Request(
                        urljoin_rfc(URL_BASE, url), 
                        headers=self.headers,
                        callback=self.parse
                        )
                yield request


        ## parse pages
        #if len(items) > 0:
            ## process next page
            #page_param_index = response.url.find("page=")
            #if page_param_index > -1:
                ## page > 1
                #page_param_index += len("page=")
                #current_page = int(response.url[page_param_index:])
                #next_page_url = response.url[:page_param_index] + str(current_page + 1)
            #else:
                #next_page_url = response.url + "&page=" + str(2)
            #request = Request(urljoin_rfc(URL_BASE, next_page_url), callback=self.parse)
            #yield request

