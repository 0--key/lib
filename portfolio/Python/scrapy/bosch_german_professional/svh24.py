import csv
import os
import copy
import re
from decimal import Decimal

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http.cookies import CookieJar

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class AmazonSpider(BaseSpider):
    name = 'bosch-german-professional-svh24.de'
    allowed_domains = ['svh24.de']
    user_agent = 'spd'

    def start_requests(self):
        with open(os.path.join(HERE, 'bosch_german_professional.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row['svh24']
                if url:
                    yield Request(url, meta={'sku': row['sku']}, callback=self.parse_product)

    def parse(self, response):
        pass

    def parse_product(self, response):

        hxs = HtmlXPathSelector(response)

        loader = ProductLoader(item=Product(), selector=hxs)
        loader.add_value('url', response.url)
        loader.add_xpath('name', u'//h1[@itemprop="name"]/text()')
        price = hxs.select(u'//span[@itemprop="price"]/text()').extract()[0].replace(',', '.')
        loader.add_value('price', price)
        loader.add_value('sku', response.meta['sku'])
        yield loader.load_item()
