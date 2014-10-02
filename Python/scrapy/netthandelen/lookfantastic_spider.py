import os
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url
from scrapy import log

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.fuzzywuzzy import process
from product_spiders.fuzzywuzzy import fuzz

from product_spiders.spiders.BeautifulSoup import BeautifulSoup

HERE = os.path.abspath(os.path.dirname(__file__))

class LookFantasticSpider(BaseSpider):
    name = 'lookfantastic.com'
    allowed_domains = ['lookfantastic.com']
    start_urls = ['http://www.lookfantastic.com/home.dept?switchcurrency=EUR']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//div[@class="nav"]/ul/li[count(div)>0]/a/@href').extract()
        for category in categories:
            yield Request(category, callback=self.parse_page)
            
    # Can either a subcategory or product listing page 
    def parse_page(self, response):
        hxs = HtmlXPathSelector(response)
        
        # Try to find subcategories
        subcats = hxs.select('//div[@class="cat-content"]/p[@class="cat-heading"]/a/@href').extract()
        if subcats:
            for subcat in subcats:
                yield Request(subcat, callback=self.parse_page)
            
        # Try to find products
        products = hxs.select('//div[contains(@class,"item-detail-list")]//div[contains(@class,"item") and contains(@class,"detail") and @rel]')
        if products:
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)
                loader.add_xpath('url', './/p[@class="product-name"]/a/@href')
                loader.add_xpath('name', './/p[@class="product-name"]/a/@title')
                loader.add_xpath('price', './/p[@class="price"]/span[@class="price-value"]/text()')
                loader.add_xpath('sku', '@rel')
                yield loader.load_item()
                
            next = hxs.select('//ul[contains(@class,"pager")]/li[contains(@class,"next")]/a/@href').extract()
            if next:
                yield Request(urljoin_rfc(response.url, next[0]), callback=self.parse_page)
