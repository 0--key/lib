import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy import log
from urllib import urlencode
import hashlib

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip\
                             as ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class JustVitaminsSpider(BaseSpider):
    name = 'justvitamins.co.uk-merckgroup'
    allowed_domains = ['www.justvitamins.co.uk', 'justvitamins.co.uk']
    start_urls = ('http://www.justvitamins.co.uk/A-Z-Product-Listing.aspx',)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # getting product links from A-Z product list
        links = hxs.select('//div[@class="Product"]/a/@href').extract()
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

        name = hxs.select('//td[@class="ProductDetails"]/h1/text()').extract()
        if name:
            name = name[0].strip()
            url = response.url
            url = urljoin_rfc(get_base_url(response), url)
            items = hxs.select('//div[@class="Item"]')
            for item in items:
                loader = ProductLoader(item=Product(), selector=item)
                loader.add_value('url', url)
                #loader.add_value('name', name[0])

                sku = ''.join(item.select('./text()').extract())
                n = name
                if sku:
                    n += ' ' + sku.strip()

                loader.add_value('name', n)
                loader.add_xpath('price', './/span[@class="price"]/text()')
                loader.add_xpath('price', './div[@class="price"]/span/text()')


                yield loader.load_item()
