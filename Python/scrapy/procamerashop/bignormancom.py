import csv
import copy
import logging
import shutil
import os

from scrapy import signals
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.xlib.pydispatch import dispatcher
from scrapy import log

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class BignormanComSpider(BaseSpider):
    name = 'bignorman.com-procamerashop'
    allowed_domains = ['bignorman.com']

    def start_requests(self):
        shutil.copy(os.path.join(os.path.dirname(HERE), 'eservicegroup/bignormancomspider.csv'),
                                 os.path.join(HERE, 'bignormancomspider.csv.' + self.name + '.cur'))
        yield Request('http://www.bignorman.com')

    def parse(self, response):
        with open(os.path.join(HERE, 'bignormancomspider.csv.' + self.name + '.cur')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                product = Product()
                loader = ProductLoader(item=product, response=response)
                loader.add_value('url', row['url'])
                loader.add_value('name', row['name'])
                loader.add_value('price', row['price'])
                yield loader.load_item()
