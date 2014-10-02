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

class SimplySupplementsSpider(BaseSpider):
    name = 'simplysupplements.net-merckgroup'
    allowed_domains = ['www.simplysupplements.net', 'simplysupplements.net']
    start_urls = ('http://www.simplysupplements.net/product-a-to-z/',)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # getting product links from A-Z product list
        links = hxs.select('//ul[@id="product-a-to-z"]/li/a/@href').extract()
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

        name = hxs.select('//div[@class="innercol"]/h1/text()').extract()
        if name:
            url = response.url
            url = urljoin_rfc(get_base_url(response), url)
            skus = hxs.select('//td[@class="size"]/strong/text()').extract()
            prices = hxs.select('//td[@class="price"]/text()').extract()
            skus_prices = zip(skus, prices)
            for sku, price in skus_prices:
                loader = ProductLoader(item=Product(), selector=hxs)
                loader.add_value('url', url)
                loader.add_value('name', name[0].strip() + ' ' + sku.strip(':'))
                #loader.add_value('sku', sku)
                loader.add_value('price', price)
                yield loader.load_item()
