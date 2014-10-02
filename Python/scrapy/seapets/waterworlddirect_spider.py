import csv
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

class WharfAquaticsSpider(BaseSpider):
    name = 'waterworlddirect.com'
    allowed_domains = ['waterworlddirect.com']
    start_urls = ['http://www.waterworlddirect.com']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//*[@id="categories"]/ul/li/div[@class="s_submenu"]/ul/li/a/@href').extract()
        for category in categories:
            yield Request(category, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="s_item grid_3"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)   
            loader.add_xpath('name', 'h3/a/text()')
            loader.add_xpath('url', 'h3/a/@href')
            price = ''.join(product.select('p[@class="s_price"]/text()').extract())
            if not price:
                price = ''.join(product.select('p[@class="s_price s_promo_price"]/text()').extract())
            loader.add_value('price', price)
            yield loader.load_item()
        next = hxs.select('//a[@class="page_next"]/@href').extract()
        if next:
            yield Request(next[0], callback=self.parse_products)
        categories = hxs.select('//div[@id="category" and @class="grid_12"]/div/div[@class="s_subcategory"]/a[1]/@href').extract()
        if categories:
            for category in categories:
                yield Request(category, callback=self.parse_products)
         
    def _get_prices(self, script):
        prices = []
        for line in script.split('";')[:-1]:
            price, desc = line.split(';')
            prices.append((price.split('=')[-1], desc.split('="')[-1]))
        return prices
