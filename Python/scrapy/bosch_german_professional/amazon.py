import csv
import os
import copy
import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http.cookies import CookieJar

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class AmazonSpider(BaseSpider):
    name = 'bosch-german-professional-amazon.de'
    allowed_domains = ['amazon.de']
    user_agent = 'spd'

    def start_requests(self):
        with open(os.path.join(HERE, 'bosch_german_professional.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row['amazon']
                if url:
                    yield Request(url, meta={'sku': row['sku']}, callback=self.parse_product)

    def parse(self, response):
        pass

    def parse_product(self, response):

        hxs = HtmlXPathSelector(response)

        loader = ProductLoader(item=Product(), selector=hxs)
        loader.add_value('url', response.url)
        loader.add_xpath('name', u'//div[@class="buying"]/h1[@class="parseasinTitle"]/span[@id="btAsinTitle"]/text()')
        price = hxs.select(u'//div[@class="buying"]/table[@class="product"]//b[@class="priceLarge"]/text()').extract()[0]
        loader.add_value('price', price.replace(',', '.'))
        loader.add_value('sku', response.meta['sku'])
        yield loader.load_item()
