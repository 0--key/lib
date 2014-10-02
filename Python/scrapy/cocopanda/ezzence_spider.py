import os
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.fuzzywuzzy import process
from product_spiders.fuzzywuzzy import fuzz

HERE = os.path.abspath(os.path.dirname(__file__))

class EzzenceSpider(BaseSpider):
    name = 'cocopanda-ezzence.dk'
    allowed_domains = ['ezzence.dk']
    start_urls = ['http://ezzence.dk/maerkeraz']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//*[@id="maerkeraz"]/ul/li/a/@href').extract()
        for category in categories:
            yield Request(category+'?limit=all', callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//ul[@class="products-grid"]/li')
        if products:
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)   
                loader.add_xpath('name', 'div/div/h2[@class="product-name"]/a/@title')
                loader.add_xpath('url', 'div/div/h2[@class="product-name"]/a/@href')
                price = ''.join(product.select('div/div/div[@class="price-box"]/span/span[@class="price"]/text()').extract()).replace('.','').replace(',','.')
                if not price:
                    price = ''.join(product.select('div/div/div[@class="price-box"]'
                                                   '/p[@class="special-price"]/'
                                                   'span[@class="price"]/text()').extract()).replace('.','').replace(',','.').strip()
                loader.add_value('price', price)
                yield loader.load_item()
