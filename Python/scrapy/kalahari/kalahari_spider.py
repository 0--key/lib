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
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

REP = [',', '.', ':', '-', '&', '?', '(', ')', '/', '"', '+', '[', ']']
def normalized_name(name):
    name = name.replace("'", '')
    for r in REP:
        name = name.replace(r, ' ')

    name = ' '.join(name.split()).strip()
    name = '-'.join(name.split())
    return name

class KalahariSpider(BaseSpider):
    name = 'kalahari.com'
    allowed_domains = ['kalahari.com']

    def start_requests(self):
        with open(os.path.join(HERE, 'products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['ProdCode']
                prod_id = row['k_sku']
                name = normalized_name(row['Title'])

                url = 'http://www.kalahari.com/home/%s/%s.aspx'
                url = url % (name, prod_id)
                yield Request(url, meta={'sku': sku, 'url': url})

    def parse(self, response):
        if '500.html' in response.url:
            retries = response.meta.get('retries', 0)
            if retries < 3:
                yield Request(response.meta['url'], dont_filter=True, meta={'sku': response.meta['sku'],
                                                                            'retries': retries + 1})

        hxs = HtmlXPathSelector(response)
        if hxs.select('//p[@class="stock_status" and text()="Out of stock"]'):
            return

        loader = ProductLoader(item=Product(), response=response)
        loader.add_xpath('name', '//h1[@class="page_heading"]/text()')
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//tr[@class="our_price"]//td[@class="amount"]/text()')
        loader.add_xpath('price', '//span[@class="price"]/text()')
        loader.add_value('sku', response.meta['sku'])

        yield loader.load_item()


