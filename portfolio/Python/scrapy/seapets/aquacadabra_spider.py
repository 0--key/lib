import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log
from urlparse import urlparse

class AquacadabraSpider(BaseSpider):
    name = 'aquacadabra.co.uk'
    allowed_domains = ['www.aquacadabra.co.uk']
    start_urls = (
                  'http://www.aquacadabra.co.uk/',
                  )
    
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        cat_urls = hxs.select('//div[@class="cdialog"]//a[@class="product-title"]/@href').extract()
        if cat_urls:
            for url in cat_urls:
                yield Request(url, callback=self.parse)
                
        product_urls = hxs.select('//div[@class="psdialog"]//a[@class="product-title" and text()="See details"]/@href').extract()
        if product_urls:
            for url in product_urls:
                yield Request(url, callback=self.parse_product)
                
        next = hxs.select('//a[@class="right-arrow" and descendant::img[@alt="Next page"]]/@href').extract()
        if next:
            yield Request(next[0], callback=self.parse)
    
    def parse_product(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        loader = ProductLoader(item=Product(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//span[@id="product_price"]/text()')
        loader.add_xpath('sku', '//td[@id="product_code"]/text()')
        yield loader.load_item()
    
    