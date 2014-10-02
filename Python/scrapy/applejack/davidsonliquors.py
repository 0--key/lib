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

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class DavidsonsLiquorsSpider(BaseSpider):
    name = 'davidsonsliquors.com'
    allowed_domains = ['www.davidsonsliquors.com', 'davidsonsliquors.com']
    start_urls = ('http://www.davidsonsliquors.com/store.asp',
                  'http://www.davidsonsliquors.com/search_results.asp?search=BALVENIE&Submit=Search')

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//a[@class="style14"]/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pagination
        next_page = hxs.select(u'//a[contains(text(),"Next")]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        # products
        for product in self.parse_product(response):
            yield product

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        products = hxs.select(u'//div[@class="style12"]/div[@align="left"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_value('url', response.url)
            name = product.select(u'.//span[@class="style12BBL"]/text()').extract()[0].strip()
            product_data = product.select(u'./text()').extract()[0].split(u'-')
            name += u' ' + product_data[1].strip()
            price = product_data[2].strip()
            loader.add_value('name', name)
            loader.add_value('price', price)
            yield loader.load_item()
