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

class EnkorSpider(BaseSpider):
    name = 'bosch-professional-enkor.ru'
    allowed_domains = ['enkor.ru']

    def start_requests(self):
        with open(os.path.join(HERE, 'enkor.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row['url']
                code = row['code']
                if code.strip():
                    yield Request(url, meta={'sku': row['sku'],
                                             'code': code.strip()}, callback=self.parse_product_1)
                else:
                    yield Request(url, meta={'sku': row['sku']}, callback=self.parse_product_2)

    def parse(self, response):
        pass

    def parse_product_2(self, response):

        hxs = HtmlXPathSelector(response)


        loader = ProductLoader(item=Product(), selector=hxs)
        loader.add_value('url', response.url)
        loader.add_xpath('name', u'//td[@width="380"]/span[1]/text()')
        price = hxs.select('//td[@width="380"]/span[2]/text()').extract()
        if price:
            #price = price[0].replace(' ', '')
            loader.add_value('price', price)
        else:
            loader.add_value('price', 0)
        loader.add_value('sku', response.meta['sku'])
        yield loader.load_item()

    def parse_product_1(self, response):
        hxs = HtmlXPathSelector(response)

        loader = ProductLoader(item=Product(), selector=hxs)
        loader.add_value('url', response.url)
        name = hxs.select('//nobr[text()="%s"]/../../td[1]//text()' % response.meta['code']).extract()
        if not name:
            return

        loader.add_value('name', ''.join(name).strip())

        price = hxs.select('//nobr[text()="%s"]/../../td[5]//text()' % response.meta['code']).extract()
        loader.add_value('price', price[1])
        loader.add_value('sku', response.meta['sku'])
        yield loader.load_item()


