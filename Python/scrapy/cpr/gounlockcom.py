from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import ProductLoader, Product
from product_spiders.utils import extract_price2uk

import logging

class GounlockComSpider(BaseSpider):
    name = 'gounlock.com'
    allowed_domains = ['gounlock.com']
    start_urls = (
        'https://www.gounlock.com/',
        )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        categories = hxs.select("//td[@class='columnLeft']/div[@id='nav']//a/@href").extract()
        for category in categories:
            url = urljoin_rfc(base_url, category)
            yield Request(url, callback=self.parse)

        items_table = hxs.select("//table[@class='productsBox']/tr/td[@class='newProducts']")
        for item in items_table:
            name = item.select("h2/a/text()").extract()
            if not name:
                logging.error("%s - ERROR! NO NAME!" % response.url)
                continue
            name = name[0]
            url = item.select("h2/a/@href").extract()
            if not url:
                logging.error("%s - ERROR! NO URL!" % response.url)
                continue
            url = url[0]
            url = urljoin_rfc(base_url, url)
            price = item.select(".//div[@class='price']/text()").extract()
            if not price:
                logging.error("%s - %s - ERROR! NO PRICE!" % (response.url,
                    name))
                continue
            price = price[-1]
            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', str(name))
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()

        items_list = hxs.select("//table[@class='cartTbl']/tr")
        for item in items_list:
            name = item.select("td[2]/a/text()").extract()
            if not name:
                logging.error("%s - ERROR! NO NAME!" % response.url)
                continue
            name = name[0]
            url = item.select("td[2]/a/@href").extract()
            if not url:
                logging.error("%s - ERROR! NO URL!" % response.url)
                continue
            url = url[0]
            url = urljoin_rfc(base_url, url)
            price = item.select("td[2]/text()").extract()
            if not price:
                logging.error("%s - %s - ERROR! NO PRICE!" % (response.url,
                    name))
                continue
            price = " ".join(price)
            if not extract_price2uk(price):
                logging.error("%s - %s - ERROR! NO PRICE!" % (response.url,
                    name))
                continue
            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', str(name))
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()

