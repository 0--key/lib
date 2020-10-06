from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import ProductLoader, Product

import logging

class FlexqueenComSpider(BaseSpider):
    name = 'flexqueen.com'
    allowed_domains = ['flexqueen.com']
    start_urls = (
        'http://www.flexqueen.com/',
        )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        categories = hxs.select("//div[@id='nav-product']//a/@href").extract()
        for category in categories:
            url = urljoin_rfc(base_url, category)
            yield Request(url, callback=self.parse)

        items_table = hxs.select("//table[@id='contents-table']/tr/td")
        sub_cats_found = 0
        items_found = 0
        for item in items_table:
            name = item.select("div[@class='name']/a/text()").extract()
            if not name:
                logging.error("%s - ERROR! NO NAME!" % response.url)
                continue
            name = name[0]
            url = item.select("div[@class='name']/a/@href").extract()
            if not url:
                logging.error("%s - ERROR! NO URL!" % response.url)
                continue
            url = url[0]
            url = urljoin_rfc(base_url, url)
            price = item.select("div[@class='sale-price-bold']/text()").extract()
            if not price:
                price = item.select("div[@class='price-bold']/text()").extract()
                if not price:
                    # Must be a subcategory
                    yield Request(url, callback=self.parse)
                    sub_cats_found += 1
                    continue
            price = price[0].split(',')[0]
            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', str(name))
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()
            items_found += 1
        if items_found == 0 and sub_cats_found == 0:
            logging.error("%s ERROR! No subcategories or products found!" %
                    response.url)

