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

class FeelUniqueSpider(BaseSpider):
    name = 'cocopanda-feelunique.com'
    allowed_domains = ['feelunique.com']
    start_urls = ['http://www.feelunique.com']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//*[@id="nav-container"]/ul/li/a/@href').extract()
        for category in categories:
            url =  urljoin_rfc(get_base_url(response), category)
            yield Request(url+'?curr=NOK', callback=self.parse_subcategories)

    def parse_subcategories(self, response):
        hxs = HtmlXPathSelector(response)
        sub_categories = hxs.select('//*[@id="leftcolumn"]/ul[1]/li/a/@href').extract()
        for sub_category in sub_categories:
            url =  urljoin_rfc(get_base_url(response), sub_category)
            yield Request(url+'?curr=NOK', callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products =  products = hxs.select('//div[@class="ProductPanel"]')
        if products:
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)   
                loader.add_xpath('name', 'h2/a/text()')
                url =  urljoin_rfc(get_base_url(response), ''.join(product.select('h2/a/@href').extract()))
                loader.add_value('url', url)
                price = ''.join(product.select('div[@class="price"]/text()').extract())
                if not price:
                    price = ''.join(product.select('div[@class="price"]/span[@class="new-price"]/text()').extract())
                loader.add_value('price', price)
                yield loader.load_item()
            next = hxs.select('//a[@class="forward"]/@href').extract()
            if next:
                url =  urljoin_rfc(get_base_url(response), next[0])
                yield Request(url, callback=self.parse_products)
        #sub_categories = hxs.select('//*[@id="contentWrapper"]/div/div[@class="categoryElement"]/a/@href').extract()
        #if sub_categories:
        #    yield Request(response.url, callback=self.parse_subcategories, dont_filter=True)
