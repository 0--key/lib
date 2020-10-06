import csv
import os
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.fuzzywuzzy import process
from product_spiders.fuzzywuzzy import fuzz

HERE = os.path.abspath(os.path.dirname(__file__))

class TedsSpider(BaseSpider):
    name = 'teds.com.au'
    allowed_domains = ['teds.com.au']
    start_urls = ['http://www.teds.com.au/brands/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//ul[@class="bare-list"]/li/a/@href').extract()
        for category in categories:
            yield Request(category, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//*[@id="products-list"]/li')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'div[@class="product-details left"]/h2/a/text()')
            price = product.select('div[@class="product-shop left"]/div/div/p/span/span/text()')
            if price:
                price = price[0]
            else:
                price = product.select('div[@class="product-shop left"]/div/div/span/text()')
                if price:
                    price = price[0]
                else:
                    price = product.select('div[@class="product-shop left"]/div/div/p/span/text()')
                    if len(price)==1:
                        price = price[0]
                    else:
                        price = price[1]
            loader.add_value('price', price)
            loader.add_xpath('url', 'div[@class="product-details left"]/h2/a/@href')
            yield loader.load_item()
        next = hxs.select('//div[@class="right-nav right"]/a/@href').extract()
        if next:
            url = next[0]
            yield Request(url, callback=self.parse_products)

        


