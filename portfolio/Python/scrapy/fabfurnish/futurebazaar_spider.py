import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

import csv, codecs, cStringIO

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class futurebazaarSpider(BaseSpider):
    USER_AGENT = "Googlebot/2.1 ( http://www.google.com/bot.html)"
    name = 'futurebazaar.com'
    allowed_domains = ['www.futurebazaar.com']
    start_urls = ('http://www.futurebazaar.com/home-living/ch/2226/',
                  'http://www.futurebazaar.com/kids-baby/ch/2707/',
                  'http://www.futurebazaar.com/electronics/ch/2458/',
                  'http://www.futurebazaar.com/supermarket/ch/2515/',
                  )
                  
    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        name = "".join(hxs.select('//div[@id="product_desc"]/h1/text()').extract()).strip()
        if not name:
            name = "".join(hxs.select('//div[@class="prod_details"]/h3/a/text()').extract()).strip()
        price = "".join(hxs.select('//td[@class="price_value forange fb f16"]/text()').re(r'([0-9\, ]+)')).strip()
        if not price:
            price = "".join(hxs.select('//td[@class="price_value fcop fb f17"]/text()').re(r'([0-9\, ]+)')).strip()
        
        if price:
            product_loader = ProductLoader(item=Product(), response=response)
            product_loader.add_value('price', price)
            product_loader.add_value('url', response.url)
            product_loader.add_value('name', name)
            yield product_loader.load_item()                  
    
    def parse(self,response):
      if not isinstance(response, HtmlResponse):
          return
            
      hxs = HtmlXPathSelector(response)
      base_url = get_base_url(response)
      
      #get cats
      cats = hxs.select('//div[@id="cat_filter"]/div/ul/li/a/@href').extract()
      for cat in cats:
          yield Request(urljoin_rfc(base_url,cat))
          
      #pages 
      pages = hxs.select('//div[@class="sort_bar"]/div[@class="right"]/span/a/@href').extract()
      for page in pages:
          yield Request(urljoin_rfc(base_url,page))
          
      products = hxs.select('//div[@class="srp_greed_view"]/ul/li/div/div/a/@href').extract()
      for p in products:
          yield Request(urljoin_rfc(base_url,p), callback=self.parse_product) 
          