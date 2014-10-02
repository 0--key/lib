import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
import hashlib

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip\
                             as ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class HealthSpanSpider(BaseSpider):
    name = 'healthspan.co.uk'
    allowed_domains = ['www.healthspan.co.uk', 'healthspan.co.uk']
    start_urls = ('http://www.healthspan.co.uk/products/',)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # getting product links from A-Z product list
        links = hxs.select('//td[@class="itemL"]/span/a/@href').extract()
        for prod_url in links:
            url = urljoin_rfc(get_base_url(response), prod_url)
            yield Request(url)

        # products
        for product in self.parse_product(response):
            yield product

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        name = hxs.select('//h1[@class="item"]/span/text()').extract()
        if name:
            url = response.url
            url = urljoin_rfc(get_base_url(response), url)
            loader = ProductLoader(item=Product(), selector=hxs)
            loader.add_value('url', url)
            loader.add_value('name', name[0])

            items = hxs.select('//div[@class="sku-details"]')
            for item in items:
                loader = ProductLoader(item=Product(), selector=hxs)
                loader.add_value('url', url)
                #loader.add_value('name', name[0])
                n = name[0].strip()
                sku = ''.join(item.select('.//span[@class="sku-description"]//text()').extract())
                if sku:
                    n += ' ' + sku.strip()

                loader.add_value('name', n)
                price = item.select('./span[@class="price"]/text()').extract()
                if price:
                    loader.add_value('price', price[0])
                else:
                    price = item.select('./span[@class="special-price"]/text()').extract()
                    loader.add_value('price', price[0])
                yield loader.load_item()