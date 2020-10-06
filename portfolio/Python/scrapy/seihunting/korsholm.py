import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
import hashlib

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

# ~/pythoncrawlers/bin/scrapy shell http://www.korsholm.dk/dk/jagt-produkter.html

class KorsholmSpider(BaseSpider):
    name = 'korsholm.dk'
    allowed_domains = ['www.korsholm.dk', 'korsholm.dk']
    start_urls = ('http://www.korsholm.dk/dk/jagt-produkter.html', )

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//span[@class="vertnav-cat"]/a/@href').extract()
        
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # products
        for product in self.parse_product(response):
            yield product

        	
        
        	
    def parse_product(self, response):
    	if not isinstance(response, HtmlResponse):
        	return
    	hxs = HtmlXPathSelector(response)
    	
    	products = hxs.select(u'//div[@class="product_box_mid"]')
	for product in products:
	    loader = ProductLoader(item=Product(), selector=product)
	    loader.add_value('url', response.url)
	    
	    price = product.select(u'.//span[@class="price"]/text()').extract()
	    price = price[0].replace('.', '').replace(',', '.').strip()
	    
	    name = product.select(u'.//h2[@class="product-name"]/a/text()').extract()
	    name = name[0].strip()
	    
	    loader.add_value('name', name)
            loader.add_value('price', price)
            if loader.get_output_value('price'):
                yield loader.load_item()
