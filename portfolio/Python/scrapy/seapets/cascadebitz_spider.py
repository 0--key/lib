import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log
from urlparse import urlparse

class CascadebitzSpider(BaseSpider):
    name = 'cascadebitz.com'
    allowed_domains = ['www.cascadebitz.com']
    start_urls = (
                  'http://www.cascadebitz.com/',
                  )
    
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        cat_urls = hxs.select('//div[@class="leftnav"]//li[@class="navelement"]//a[descendant::img]/@href').extract()
        for url in cat_urls:
            if(urlparse(url).scheme == ''):
                url = urljoin_rfc(base_url, url)
            yield Request(url, callback=self.parse_cat)
    
    
    def parse_cat(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        subcat_urls = hxs.select('//table[@class="subCatNav"]//a[descendant::img]/@href').extract()
        for url in subcat_urls:
            if(urlparse(url).scheme == ''):
                url = urljoin_rfc(base_url, url)
            yield Request(url, callback=self.parse_subcat)
    
    
    def parse_subcat(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        product_urls = hxs.select('//div[@class="productImgDIV"]//a[descendant::img]/@href').extract()
        for url in product_urls:
            if(urlparse(url).scheme == ''):
                url = urljoin_rfc(base_url, url)
            yield Request(url, callback=self.parse_product)
            
    
    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
    
        items = hxs.select('//table[@class="pricecart"]//tr')
        for item in items:
            loader = ProductLoader(item=Product(), selector=item)
            loader.add_xpath('name', './/span[@class="spanDescription"]/text()')
            loader.add_value('url', response.url)
            loader.add_value('price', item.select('.//td[@class="cellPrice"]/text()').re('Our Price\s+.?(\d+(?:\.\d+))')[0])
            loader.add_value('sku', item.select('.//td[@class="cellAddToCart"]/a/@href').re('pid=([0-9a-f]+)')[0])
            yield loader.load_item()
    