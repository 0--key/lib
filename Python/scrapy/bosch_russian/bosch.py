import csv
import os

import json  
from string import join

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

HERE = os.path.abspath(os.path.dirname(__file__))

class Bosch (BaseSpider):

	base_url = "http://www.bosch.ru/"
	name = 'bosch.ru'
	allowed_domains = ['bosch.ru']
	start_urls = [base_url]

	def parse(self, response):
		hxs = HtmlXPathSelector()
		with open(os.path.join(HERE, 'bosh_products.csv')) as f:
			reader = csv.DictReader(f)
			for row in reader:
				product_loader = ProductLoader(item=Product(), selector=hxs)
				product_loader.add_value('name', unicode(row['name'],'utf-8'))
				product_loader.add_value('price',row['price'])
				product_loader.add_value('sku',row['sku'])
				yield product_loader.load_item()

