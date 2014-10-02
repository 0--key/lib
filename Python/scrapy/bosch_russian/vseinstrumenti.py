import csv
import os

import json  
from string import join

from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class VseInstrumenti(BaseSpider):

	base_url = "http://www.vseinstrumenti.ru/"
	name = 'vseinstrumenti.ru'
	allowed_domains = ['vseinstrumenti.ru']
	start_urls = [base_url]

	def start_requests(self):
		with open(os.path.join(HERE, 'bosh_products.csv')) as f:
			reader = csv.DictReader(f)
			for row in reader:
				sku = row['sku'].strip()
				name = row['name'].strip()
				url = 'http://www.vseinstrumenti.ru/pre_search.php?make=0&term=%s'
				yield Request(url % sku, meta={'sku': sku, 'name': name, 'search_by':'sku'})


	def parse(self, response):

		if response.body.strip() == "":
			if response.meta['search_by']=='sku':
				#search by name
				url = 'http://www.vseinstrumenti.ru/pre_search.php?make=0&term=%s'
				return Request(url % response.meta['name'].replace(" ","+"), callback=self.parse, meta={'sku': response.meta['sku'], 'name': response.meta['name'], 'search_by':'name'})
		else:
			jdata = json.loads(response.body)
			for jd in jdata:
				if response.meta['sku'].decode('utf-8') in jd['label'].replace(".","") or response.meta['name'].decode('utf-8') in jd['label']:
					try:
						log.msg("LINK:"+jd['link'])
						return Request(jd['link'], callback=self.parse_product, meta={'sku': response.meta['sku'], 'name':jdata[0]['label']} )
					except ValueError:
						return Request((self.base_url+jdata[0]['link']).replace('.ru//', '.ru/'), callback=self.parse_product, meta={'sku': response.meta['sku'], 'name':jdata[0]['label']} )						

	def parse_product(self, response):
		hxs = HtmlXPathSelector(response)
		price = join(hxs.select(u'//div[contains(@class, "goods_price")]/text()').extract())
		price = price.strip().replace(" ","")

		product_loader = ProductLoader(item=Product(), selector=hxs)
		product_loader.add_value('name', response.meta["name"])
		product_loader.add_value('url', response.url)
		product_loader.add_value('price', price)
		product_loader.add_value('sku', response.meta["sku"])
		if product_loader.get_output_value('price'):			
			return product_loader.load_item()

