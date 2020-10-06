from string import join

import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse

from product_spiders.items import Product, ProductLoader

class OutillageSpider(BaseSpider):
	
	name = "outillage2000"
	base_url = "http://www.outillage2000.com/"
	allowed_domains = ["outillage2000.com"]
	start_urls = [base_url]

	def parse(self, response):

		hxs = HtmlXPathSelector(response)

		# categories
		categories = hxs.select(u'//div[@class="niveau_0"]')
		
		for cat in categories:
			cat_url = join(cat.select(u'div/a/@href').extract())
			num_products = join(cat.select(u'div/a/span/text()').extract())
			if num_products=="" and cat_url == self.base_url:
				continue

			yield Request(cat_url)
	
		#subcategories
		subcategories=hxs.select(u'//div[@class="niveau_1"]')

		for subcat in subcategories:	
			subcat_url = join(subcat.select(u'div/a/@href').extract())
			yield Request(subcat_url)

		#next-pages
		pages=hxs.select(u'//div[@class="splitPageL"]/a')

		for page in pages:			
			page_url = join(page.select(u'@href').extract())
			title = join(page.select(u'@title').extract())
			#skip last page (>>)
			if title.strip() == "Page suivante":
				continue
			
			yield Request(page_url)

		#products
		products=hxs.select(u'//div[contains(@class,"product-container")]')
		for product in products:
			product_url = join(product.select(u'div[@class="product-image"]/a/@href').extract())
			yield Request(product_url)

		#if there is a boxMaster, where the subproducts are listed call parse_subproduct, else call parse_product
		boxMaster =join(hxs.select(u'//div[@id="boxMaster"]/@class').extract())
		if len(boxMaster ) > 0:
			subproducts=hxs.select(u'//form[@name="buy_now"]/div[@class="boxContent"]/table/tr')
			for subprod in subproducts:		
				for main_product in self.parse_subproduct(subprod):
					yield main_product
		else:
			for main_product in self.parse_product(response):
				yield main_product

			
	def parse_subproduct (self, subprod):
		if not isinstance(subprod, HtmlXPathSelector):
			return

		url= join(subprod.select(u'td[1]/a/@href').extract())
		name = join(subprod.select(u'td[1]/a/@title').extract())
		price = join(subprod.select(u'td[3]/text()').extract())

		#remove euro sign and replace ',' with '.' in the price				
		price = price.replace(u',',u'.').replace(u'\xe2',u"").strip()

		# if there is a discount the price is in another element		
		if price is None or len(price) == 0 :
			price = join(subprod.select(u'td[3]/ins/text()').extract())
			price = price.replace(u',',u'.').replace(u'\xe2',u"").strip()

		#strip html tags from name
		name = re.sub('<[^<]+?>', '',name)

		product_loader = ProductLoader(item=Product(), selector=subprod)
		product_loader.add_value('name', name)
		product_loader.add_value('url', url)
		product_loader.add_value('price', price)
		if product_loader.get_output_value('name'):			
			yield product_loader.load_item()

	def parse_product(self, response):
		if not isinstance(response, HtmlResponse):
			return

		hxs = HtmlXPathSelector(response)		
		url=response.url
		name = join(hxs.select(u'//h1[@id="titre_produit"]/text()').extract())
		price = join(hxs.select(u'//div[@id="productPrice"]/text()').extract())
		#remove euro sign and replace ',' with '.' in the price
		price = price.replace(u',',u'.').replace(u'\xe2',u"").strip()
		# if there is a discount the price is in another element		
		if price is None or len(price) == 0 :
			price = join(hxs.select(u'//div[@id="productPrice"]/ins/text()').extract())
			price = price.replace(u',',u'.').replace(u'\xe2',u"").strip()

		#strip html tags from name
		name = re.sub('<[^<]+?>', '',name)
		product_loader = ProductLoader(item=Product(), selector=name)
		product_loader.add_value('name', name)
		product_loader.add_value('url', url)
		product_loader.add_value('price', price)
		if product_loader.get_output_value('name'):			
			yield product_loader.load_item()
