from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import ProductLoader, Product

import logging

class WirelesspartsincComSpider(BaseSpider):
    name = 'wirelesspartsinc.com'
    allowed_domains = ['wirelesspartsinc.com']
    start_urls = (
        'https://www.wirelesspartsinc.com/',
        )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        categories = hxs.select("//table[@class='module category-module']//a/@href").extract()
        for category in categories:
            url = urljoin_rfc(base_url, category)
            yield Request(url, callback=self.parse)

        sub_categories = hxs.select("//table[@class='category-list']//a/@href").extract()
        for sub_category in sub_categories:
            url = urljoin_rfc(base_url, sub_category)
            yield Request(url, callback=self.parse)

        pages = hxs.select("//table[@class='product-pager']//a/@href").extract()
        for page in pages:
            url = urljoin_rfc(base_url, page)
            yield Request(url, callback=self.parse)

        items_table = hxs.select("//table[@class='product-list']/tr/td/div[@class='product-list-item']")
        for item in items_table:
            name = item.select("div[@class='product-list-options']/h5/a/text()").extract()
            if not name:
                logging.error("%s - ERROR! NO NAME!" % response.url)
                continue
            name = name[0]
            url = item.select("div[@class='product-list-options']/h5/a/@href").extract()
            if not url:
                logging.error("%s - ERROR! NO URL!" % response.url)
                continue
            url = url[0]
            url = urljoin_rfc(base_url, url)
            price = item.select("div[@class='product-list-options']/div[@class='product-list-price']/\
                                 div[@class='product-list-cost']/span[@class='product-list-cost-value']/text()").extract()
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

