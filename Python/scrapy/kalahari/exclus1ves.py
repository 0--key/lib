import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class Exclus1vesSpider(BaseSpider):
    name = 'exclus1ves.co.za'
    allowed_domains = ['exclus1ves.co.za']
    user_agent = 'GoogleBot'

    def start_requests(self):
        with open(os.path.join(HERE, 'products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['ProdCode']
                if not row['ProductType'] in ['Books', 'eBooks', 'Music', 'DVD/Video', 'Games']:
                    continue

                url = 'http://www.exclus1ves.co.za/search/?q=%s'
                yield Request(url % sku, meta={'sku': sku})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        product = hxs.select('//div[@class="product-detail-information"]')
        if not product:
            return

        product = product[0]
        loader = ProductLoader(item=Product(), selector=product)
        loader.add_xpath('name', './/h1[contains(@class,"product-title")]/a/text()')
        loader.add_value('url', response.url)
        price = ''.join(hxs.select('.//h5[@class="price price-lowest"]//text()').extract())
        loader.add_value('price', price)
        loader.add_value('sku', response.meta['sku'])

        yield loader.load_item()

