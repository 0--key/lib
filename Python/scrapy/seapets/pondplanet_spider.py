import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log
from urlparse import urlparse

class PondplanetSpider(BaseSpider):
    name = 'pond-planet.co.uk'
    allowed_domains = ['www.pond-planet.co.uk']
    start_urls = (
                  'http://www.pond-planet.co.uk/',
                  )
    
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        cat_urls = hxs.select('//ul[@id="suckertree1"]//li[not(descendant::ul)]/a/@href').extract()
        for url in cat_urls:
            yield Request(url, callback=self.parse_cat)
        
    def parse_cat(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        product_urls = hxs.select('//table[@class="productListing"]/tr[contains(@class,"productListing")]/td/a[not(descendant::img)]/@href').extract()
        for url in product_urls:
            yield Request(url, callback=self.parse_product)
    
    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        
        price = hxs.select('//h1/span[@class="productSpecialPrice"]/text()').extract()
        if(not price):
            price = hxs.select('//td[@align="right"]/h1/text()').extract()
        
        loader = ProductLoader(item=Product(), response=response)
        loader.add_xpath('name', '//td[@valign="top" and not(@align="right")]/h1/text()')
        loader.add_value('url', response.url)
        loader.add_value('price', price[0])
        loader.add_xpath('sku', '//input[@name="products_id"]/@value')
        yield loader.load_item()

