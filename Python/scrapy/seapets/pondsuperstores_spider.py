import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log

class PondsuperstoresSpider(BaseSpider):
    name = 'pondsuperstores.com'
    allowed_domains = ['www.pondsuperstores.com']
    start_urls = (
                  'http://www.pondsuperstores.com/brands/',
                  )
    
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        brand_urls = hxs.select('//form[@id="frmCompare"]//a[@class="brandlink"]/@href').extract()
        for url in brand_urls:
            yield Request(url, callback=self.parse_brand)

    def parse_brand(self, response):
        hxs = HtmlXPathSelector(response)
        
        product_urls = hxs.select('//form[@id="frmCompare"]//div[@class="ProductDetails"]//a/@href').extract()
        for url in product_urls:
            yield Request(url, callback=self.parse_product)
            
        next = hxs.select('//div[@class="CategoryPagination"]//a[contains(text(),"Next")]/@href').extract()
        if next:
            yield Request(next[0], callback=self.parse_brand)
        
    
    def parse_product(self, response):        
        loader = ProductLoader(item=Product(), response=response)
        loader.add_xpath('name', '//div[@id="ProductDetails"]//h2/text()')
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//div[@id="ProductDetails"]//em[contains(@class,"ProductPrice")]/text()')
        loader.add_xpath('sku', '//div[@id="ProductDetails"]//span[contains(@class,"VariationProductSKU")]/text()')
        yield loader.load_item()
        