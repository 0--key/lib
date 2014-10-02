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

HERE = os.path.abspath(os.path.dirname(__file__))

class Bosch (BaseSpider):
    base_url = "http://www.bosch-professional.com"
    name = 'bosch-professional.com-pl'
    allowed_domains = ['bosch-professional.com']
    start_urls = [base_url]

    def start_requests(self):
        with open(os.path.join(HERE, 'bosch_polish_professional.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row['bosch']
                if url:
                    yield Request(url, meta={'sku': row['sku'], 'name': row['name']}, callback=self.parse_product)

    def parse(self, response):
        pass

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        loader = ProductLoader(item=Product(), selector=hxs)
        loader.add_value('name', response.meta['name'])
        price = hxs.select(u'//div[@id="purchaseProc"]//span/text()').extract()[0]
        loader.add_value('price', price.replace('.', '').replace(',', '.'))
        loader.add_value('sku',response.meta['sku'])
        loader.add_value('url',response.url)
        yield loader.load_item()
