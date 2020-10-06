import csv
import os

import json  
from string import join

from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class Enkor(BaseSpider):

	base_url = "http://www.enkor.ru/"
	name = 'enkor.ru'
	allowed_domains = ['enkor.ru']
	start_urls = [base_url]

	def start_requests(self):
		with open(os.path.join(HERE, 'bosh_products.csv')) as f:
			reader = csv.DictReader(f)
			for row in reader:
				sku = row['sku'].strip()
				if sku == "603264508":
						log.msg("BBBB", log.DEBUG)					
				enkor_sku = row['enkor_sku']
				name = row['name'].strip().replace("(","").replace(")","")
				if enkor_sku:
					url = 'http://www.enkor.ru/?i=search_rozn&s_go=1&input_name=%s&select_input=2'
					yield Request(url % enkor_sku.strip(), meta={'sku': sku, 'name': name})	
				else:
					url = 'http://www.enkor.ru/?i=search_rozn&s_go=1&input_name=%s&select_input=0'
					yield Request(url % name.replace("L-BOXX", ""), meta={'sku': sku, 'name': name})

	def parse(self, response):
		hxs = HtmlXPathSelector(response)

		# categories
		products = hxs.select(u'//tr[@class="table03"]')
		# if only on product is found
		if len(products) == 1:
			for product in products:
				url = join(product.select(u'td[1]/a/@href').extract())
				if len(url) != 0:
					url = urljoin_rfc(self.base_url, url)
				name = join(product.select(u'td[1]/a/text()').extract())
				if len(name) == 0:
					name = join(product.select(u'td[1]/text()').extract())
				price = join(product.select(u'td[5]/strong/nobr/text()').extract())
				#log.msg(price, log.DEBUG)
				
				if len(url) == 0:
					url = response.url
				product_loader = ProductLoader(item=Product(), selector=product)
				product_loader.add_value('name', name)
				product_loader.add_value('url', url)
				product_loader.add_value('price', price)
				product_loader.add_value('sku', response.meta["sku"])
				return product_loader.load_item()

		# if more than one product is found
		if len(products) > 1:
			product_match = {}
			full_product_list = {}
			#iterate through all search results
			for product in products:
				url = join(product.select(u'td[1]/a/@href').extract())
				if len(url) != 0:
					url = urljoin_rfc(self.base_url, url)
				name = join(product.select(u'td[1]/a/text()').extract()).strip()
				if len(name) == 0:
					name = join(product.select(u'td[1]/text()').extract()).strip()
				if len(name) == 0:
					break
				log.msg(name, log.DEBUG)
				price = join(product.select(u'td[5]/strong/nobr/text()').extract())

				name_arr = name.split(" ")
				csv_name_arr = response.meta["name"].split(" ")
				words_match = 0.0
				# count the matching words from the search result in the products from the CSV
				for word in name_arr:
					for csv_word in csv_name_arr:
						if word.lower() == csv_word.lower() and word.strip()!= "":
							words_match = words_match+1
							log.msg(word+" in "+response.meta["name"], log.DEBUG)

				# continue if less words match that the number of words in the CSV name
				if words_match<len(csv_name_arr):
					continue

				product_match[name] = words_match/(len(name_arr)+len(name))

				log.msg(name+" : "+str(words_match)+" : "+str((len(name_arr)+len(name))), log.DEBUG)
				full_product_list[name] = {'url': url, 'price': price}

			# the search result with the highest word matches per length and words is selected as the best choice
			for key, value in sorted(product_match.iteritems(), reverse=True, key=lambda (k,v): (v,k)):

	
				product_loader = ProductLoader(item=Product(), selector=products)
				product_loader.add_value('name', key)
				product_loader.add_value('url', full_product_list[key]['url'])
				product_loader.add_value('price', full_product_list[key]['price'])
				product_loader.add_value('sku', response.meta["sku"])
				if not product_loader.get_output_value('url'):
					product_loader.add_value('url', response.url)

				return product_loader.load_item()
				break
