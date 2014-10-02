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

class Office1WebSpider(BaseSpider):
    name = 'office1web.ie'
    allowed_domains = ['www.office1web.ie', 'office1web.ie']
    start_urls = ('http://www.office1web.ie/categories',)

    def __init__(self, *args, **kwargs):
        super(Office1WebSpider, self).__init__(*args, **kwargs)
        self.skus = {}
        with open(os.path.join(HERE, 'officespot_skus.csv'), 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                self.skus[row[0]] = row[1]

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//a[contains(text(),"View All")]/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pagination
        next_page = hxs.select(u'//a[@title="Next Page" and contains(text(),"[NEXT]")]/@href').extract()
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

        products = hxs.select(u'//div[@class="product_info"]')
        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//div[@class="description"]/h4/a/@href').extract()
            url = urljoin_rfc(get_base_url(response), url[0])
            product_loader.add_value('url', url)
            sku = product.select(u'.//div[@class="description"]/p/a/text()').re(u'Code: (.*)')
            if sku:
                sku = sku[0].strip()
            if sku in self.skus:
                product_loader.add_value('sku', self.skus[sku])
            product_loader.add_xpath('name', u'.//div[@class="description"]/h4/a/text()')
            product_loader.add_xpath('price', u'.//p[@class="our_price"]/text()')
            yield product_loader.load_item()