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

class WarehouseAquaticsSpider(BaseSpider):
    name = 'warehouse-aquatics.co.uk'
    allowed_domains = ['warehouse-aquatics.co.uk']
    start_urls = ['http://www.warehouse-aquatics.co.uk/catalog/seo_sitemap/category/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//ul[@class="sitemap"]/li[@class="level-0"]/a/@href').extract()
        for category in categories:
            yield Request(category+'?limit=all', callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//*[@id="products-list"]/li')
        if products:
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)   
                loader.add_xpath('name', 'div/div/h2/a/text()')
                loader.add_xpath('url', 'div/div/h2/a/@href')
                price = ''.join(product.select('div/div/div[@class="price-box"]/span/span/text()').extract())
                if not price:
                    price = ''.join(product.select('div/div/div[@class="price-box"]/span[@class="price"]/text()').extract())
                    if not price:
                        price = ''.join(product.select('div/div/div/'
                                                       'p[@class="special-price"]/'
                                                       'span[@class="price"]/text()').extract())
                loader.add_value('price', price)
                yield loader.load_item()
        else:
            sub_categories = hxs.select('//a[descendant::span[@class="subcat"]]/@href').extract()
            for sub_category in sub_categories:
                url =  urljoin_rfc(get_base_url(response), sub_category)
                yield Request(url+'?limit=all', callback=self.parse_products)
        
