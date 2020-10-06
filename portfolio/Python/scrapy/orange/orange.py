import csv
import os

import json  
from string import join

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

HERE = os.path.abspath(os.path.dirname(__file__))

class OrangeSpider(BaseSpider):

    base_url = "http://www.orange.ch/"
    name = 'orange.ch'
    allowed_domains = ['orange.ch']
    start_urls = [base_url]

    def parse(self, response):
        hxs = HtmlXPathSelector()
        with open(os.path.join(HERE, 'orange_products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                loader = ProductLoader(item=Product(), selector=hxs)
                name = u'%s %s %s' % (row['product_name'], row['abo_name'], row['abo_duration'])
                loader.add_value('name', name)
                loader.add_value('price',row['price'])
                loader.add_value('url',row['url'])
                yield loader.load_item()
