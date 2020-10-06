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

class RedcoonSpider(BaseSpider):
    name = 'bosch-polish-professional-redcoon.pl'
    allowed_domains = ['redcoon.pl']
    user_agent = 'spd'

    def start_requests(self):
        with open(os.path.join(HERE, 'bosch_polish_professional.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row['redcoon']
                if url:
                    yield Request(url, meta={'sku': row['sku']}, callback=self.parse_product)

    def parse(self, response):
        pass

    def parse_product(self, response):

        hxs = HtmlXPathSelector(response)

        price = hxs.select(u'//p[@class="pd-price"]/img[not(contains(@src,"small"))]/@alt').extract()
        price_small = hxs.select(u'//p[@class="pd-price"]/img[contains(@src,"small")]/@alt').extract()
        price = ''.join(price)
        price_small = re.sub(u'[^\d]', u'', u''.join(price_small))
        price += price_small
        price = price.replace(',', '.')

        name = hxs.select(u'//h1[@class="pagetitle"]/span/text()').extract()
        name = map(lambda x: x.strip(), name)
        name = ' '.join(name)

        loader = ProductLoader(item=Product(), selector=hxs)
        loader.add_value('url', response.url)
        loader.add_value('name', name)
        loader.add_value('price', price)
        loader.add_value('sku', response.meta['sku'])
        yield loader.load_item()

