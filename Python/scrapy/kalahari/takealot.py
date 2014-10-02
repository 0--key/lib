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

class TakeALotSpider(BaseSpider):
    name = 'takealot.com'
    allowed_domains = ['takealot.com']

    def start_requests(self):
        with open(os.path.join(HERE, 'products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['ProdCode']
                url = 'http://www.takealot.com/all/?qsearch=%s&order=price&direction=asc'
                yield Request(url % sku, meta={'sku': sku})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        product = hxs.select('//li[@class="result-item hproduct"]')
        if not product:
            return

        product = product[0]
        loader = ProductLoader(item=Product(), selector=product)
        loader.add_xpath('name', './/p[@class="p-title fn"]/a/text()')
        url = hxs.select('.//p[@class="p-title fn"]/a/@href').extract()[0]
        loader.add_value('url', urljoin_rfc(get_base_url(response), url))
        loader.add_xpath('price', './/span[@class="amount"]/text()')
        loader.add_value('sku', response.meta['sku'])

        yield loader.load_item()
