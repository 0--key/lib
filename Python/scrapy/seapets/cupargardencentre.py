import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log
from urlparse import urlparse

class CuparGardenCentre(BaseSpider):
    name = 'cupargardencentre.co.uk'
    allowed_domains = ['www.cupargardencentre.co.uk']
    start_urls = (
                  'http://cupargardencentre.co.uk/',
                  )
    
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        cat_urls = hxs.select('//ul[@id="vmenu_8"]//li[not(descendant::ul)]/a/@href').extract()
        for url in cat_urls:
            yield Request(urljoin_rfc(base_url, url), callback=self.parse_cat)
            
    def parse_cat(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        product_divs = hxs.select('//div[@class="product-info"]')
        for product in product_divs:
            url = product.select('.//a[@class="product-title"]/@href').extract()[0];
            
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', './/a[@class="product-title"]/text()')
            loader.add_value('url', urljoin_rfc(base_url, url))
            loader.add_xpath('price', './/span[@class="price"]/span[@id]/text()')
            loader.add_xpath('sku', './/p[@class="sku"]//span[contains(@id,"product_code")]/text()')
            yield loader.load_item()
    
    