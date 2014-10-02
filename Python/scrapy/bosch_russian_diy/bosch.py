import csv
import os

import json
from string import join

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

HERE = os.path.abspath(os.path.dirname(__file__))

class Bosch (BaseSpider):

    base_url = "http://www.bosch-do-it.ru"
    name = 'bosch-diy.com-ru'
    allowed_domains = ['bosch-do-it.ru']
    start_urls = [base_url]

    def parse(self, response):
        hxs = HtmlXPathSelector()
        with open(os.path.join(HERE, 'bosch_russian_diy.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                loader = ProductLoader(item=Product(), selector=hxs)
                loader.add_value('name', unicode(row['name'],'utf-8'))
                loader.add_value('price',row['price'])
                loader.add_value('sku',row['sku'])
                loader.add_value('url',row['url'])
                yield loader.load_item()
