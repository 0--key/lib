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

class NiceHairSpider(BaseSpider):
    name = 'nicehair.dk'
    allowed_domains = ['nicehair.dk']
    start_urls = ['http://nicehair.dk']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//*[@id="narrow-by-list"]/dt/a/@href').extract()
        for category in categories:
            yield Request(category.replace('#nav','?limit=all'), callback=self.parse_products)
    
    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="grid-second"]/ul/li')
        if products:
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)   
                loader.add_xpath('name', 'h5/a/text()')
                loader.add_xpath('url', 'h5/a/@href')
                price = ''.join(product.select('div[@class="price"]/b/text()').extract()).replace('.','').replace(',','.')
                loader.add_value('price', price)
                yield loader.load_item()
        else:
            sub_categories = hxs.select('//div[@class="cats"]/center/a/@href').extract()
            for sub_category in sub_categories:
                url =  urljoin_rfc(get_base_url(response), sub_category)
                yield Request(url+'?limit=all', callback=self.parse_products)

