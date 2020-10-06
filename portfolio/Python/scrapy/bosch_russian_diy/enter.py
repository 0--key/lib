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

class EnterSpider(BaseSpider):
    name = 'bosch-diy-enter.ru'
    allowed_domains = ['enter.ru']

    def start_requests(self):
        with open(os.path.join(HERE, 'enter.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row['url']
                if url:
                    yield Request(url, meta={'sku': row['sku']}, callback=self.parse_product, dont_filter=True)

    def parse(self, response):
        pass

    def parse_product(self, response):

        hxs = HtmlXPathSelector(response)


        loader = ProductLoader(item=Product(), selector=hxs)
        loader.add_value('url', response.url)
        loader.add_xpath('name', u'//h1/text()')
        price = hxs.select('//span[@class="price"]/text()').extract()
        if price:
            price = price[0].replace(' ', '')
            loader.add_value('price', price)
        else:
            loader.add_value('price', 0)
        loader.add_value('sku', response.meta['sku'])
        yield loader.load_item()

