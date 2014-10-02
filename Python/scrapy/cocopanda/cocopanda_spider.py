import re
import os
import json

from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import XMLFeedSpider
from scrapy.selector import XmlXPathSelector
from scrapy.http import Request, XmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
import hashlib
from decimal import Decimal

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class CocopandaSpider(XMLFeedSpider):
    name = 'cocopanda.dk'
    allowed_domains = ['cocopanda.dk']
    start_urls = ('http://www.cocopanda.dk/kelkoo.xml',)
    itertag = 'product'

    def parse_node(self, response, node):
        if not isinstance(response, XmlResponse):
            return
        loader = ProductLoader(item=Product(), selector=node)
        url = node.select(u'./product-url/text()').extract()[0]
        loader.add_value('sku', url.split('/')[-2])
        loader.add_value('url', url)
        loader.add_xpath('name', u'./title/text()')
        price = node.select(u'./price/text()').extract()[0].replace(',', '.')
        loader.add_value('price', price)
        if loader.get_output_value('price'):
            return loader.load_item()
        else:
            return Product()
