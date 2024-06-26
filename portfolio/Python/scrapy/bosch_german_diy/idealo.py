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

class IdealoSpider(BaseSpider):
    name = 'bosch-german-diy-idealo.de'
    allowed_domains = ['idealo.de']

    def start_requests(self):
        with open(os.path.join(HERE, 'bosch_german_diy.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row['idealo']
                if url:
                    yield Request(url, meta={'sku': row['sku']}, callback=self.parse_product, dont_filter=True)

    def parse(self, response):
        pass

    def parse_product(self, response):

        hxs = HtmlXPathSelector(response)

        prices = hxs.select(u'//div[starts-with(@id, "opp")]/a[@class="b"]/text()').extract()
        prices = map(lambda x: re.sub(u'[^\d,\.]', '', x), prices)
        prices = map(lambda x: re.sub(u',', '.', x), prices)
        prices = map(Decimal, prices)

        loader = ProductLoader(item=Product(), selector=hxs)
        loader.add_value('url', response.url)
        loader.add_xpath('name', u'//h1/strong/text()')
        loader.add_value('price', str(min(prices)))
        loader.add_value('sku', response.meta['sku'])
        yield loader.load_item()
