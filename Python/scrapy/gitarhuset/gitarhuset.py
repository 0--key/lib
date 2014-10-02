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

class GuitarHusetpider(XMLFeedSpider):
    name = 'gitarhuset.no'
    allowed_domains = ['gitarhuset.no']
    start_urls = ('http://www.gitarhuset.no/kelkoo.xml',)
    itertag = 'product'

    def parse_node(self, response, node):
        if not isinstance(response, XmlResponse):
            return

        loader = ProductLoader(item=Product(), selector=node)
        loader.add_xpath('url', u'./product-url/text()')
        loader.add_xpath('name', u'./title/text()')
        price = node.select(u'./price/text()').extract()[0].replace(',', '.')
        loader.add_value('price', price)
        log.msg(json.dumps({'name': loader.get_output_value('name'), 'price': price}))
        if loader.get_output_value('price'):
            return loader.load_item()
        else:
            return Product()