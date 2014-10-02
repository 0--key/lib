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

class ZansaarSpider(BaseSpider):
    USER_AGENT = "Googlebot/2.1 ( http://www.google.com/bot.html)"
    name = 'zansaar.com'
    allowed_domains = ['www.zansaar.com']
    start_urls = ('http://www.zansaar.com/collections',
                  'http://www.zansaar.com/bed-bath-c-10',
                  'http://www.zansaar.com/kitchen-food-c-11',
                  'http://www.zansaar.com/world-foods-c-1116',
                  'http://www.zansaar.com/dining-entertaining-c-12',
                  'http://www.zansaar.com/accents-c-14',
                  'http://www.zansaar.com/outdoor-c-15',
                  'http://www.zansaar.com/kids-c-16',
                  )
                  
    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        name = "".join(hxs.select('//h1[@id="pdp_title"]/text()').extract()).strip()
        price = "".join(hxs.select('//section[@id="pricesection"]/h2/strong/text()').re(r'([0-9\, ]+)')).strip()
        
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
      cats = hxs.select('//nav[@class="nav"]/section/ul/li/a/@href').extract()
      for cat in cats:
          yield  Request(urljoin_rfc(base_url,cat))
          
      #pages 
      pages = hxs.select('//section[@class="paging"]/ul/li[@class="next"]/a/@href').extract()
      for page in pages:
          yield Request(page)
          
      products = hxs.select('//section[@class="product-list "]/ul/li/hgroup/h3/a/@href').extract()
      for p in products:
          yield Request(p, callback=self.parse_product)
          
      products = hxs.select('//section[@class="product-list"]/ul/li/hgroup/h3/a/@href').extract()
      for p in products:
          yield Request(p, callback=self.parse_product)          
          