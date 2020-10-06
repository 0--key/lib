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

class HomeShop18Spider(BaseSpider):
    USER_AGENT = "Googlebot/2.1 ( http://www.google.com/bot.html)"
    name = 'homeshop18.com'
    allowed_domains = ['www.homeshop18.com']
    start_urls = ('http://www.homeshop18.com/home-kitchen/category:3503/',
                  'http://www.homeshop18.com/household-appliances/category:3575/',
                  'http://www.homeshop18.com/toys-games/category:3335/',
                  'http://www.homeshop18.com/kids-26-baby/category:3627/',
                  'http://www.homeshop18.com/gifts-flowers/category:3011/',
                  'http://www.homeshop18.com/electronics/category:3203/',
                  'http://www.homeshop18.com/jewellery-watches/category:3376/',
                  'http://www.homeshop18.com/camera-26-camcorders/category:3159/',
                  'http://www.homeshop18.com/computer-peripherals/category:3254/',
                  )
                  
    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        name = "".join(hxs.select('//h1[@id="productLayoutForm:pbiName"]/text()').extract()).strip()
        price = "".join(hxs.select('//span[@id="productLayoutForm:OurPrice"]/text()').re(r'([0-9\, ]+)')).strip()
        
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
      cats = hxs.select('//ul[@id="tree"]/li/ul/li/a/@href').extract()
      for cat in cats:
          yield Request(cat.strip())
          
      #pages 
      pages = hxs.select('//div[@class="pagination"]/span/span/a/@href').extract()
      for page in pages:
          yield Request(page.strip())
          
      products = hxs.select('//div[@class="product_div"]/p/a/@href').extract()
      for p in products:
          yield Request(p.strip(), callback=self.parse_product) 
          