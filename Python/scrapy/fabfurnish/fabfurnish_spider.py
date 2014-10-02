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

class fabfurnishSpider(BaseSpider):
    USER_AGENT = "Googlebot/2.1 ( http://www.google.com/bot.html)"
    name = 'fabfurnish.com'
    allowed_domains = ['www.fabfurnish.com']
    start_urls = ('http://www.fabfurnish.com/',)

    def parse(self, response):
      hxs = HtmlXPathSelector(response)
      base_url = get_base_url(response)

      pages = hxs.select('//div[@id="Categories"]//a/@href').extract()
      pages += hxs.select('//div[@class="nav-sub"]//a/@href').extract()
      pages += hxs.select('//a[@title="Next"]/@href').extract()
      for page in pages:
          yield Request(urljoin_rfc(base_url,page))
      
      poducts = hxs.select('//ul[@id="productsCatalog"]/li/a/@href').extract()
      for poduct in poducts:
          yield Request(urljoin_rfc(base_url,poduct),callback=self.parse_product)      
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        price = "".join(hxs.select('//span[@id="product_special_price"]/text()').re(r'([0-9\, ]+)')).strip()
        if not price:
            price = "".join(hxs.select('//span[@id="price_box"]/text()').re(r'([0-9\, ]+)')).strip()
        
        if price:
            name = hxs.select('//span[@class="prd-title fsxl"]/text()').extract()[0]
            product_loader = ProductLoader(item=Product(), response=response)
            product_loader.add_value('price', price)
            product_loader.add_value('url', response.url)
            product_loader.add_value('name', name)
            return product_loader.load_item()