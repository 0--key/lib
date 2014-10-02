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

class SwellukSpider(BaseSpider):
    name = 'swelluk.com'
    allowed_domains = ['swelluk.com']
    start_urls = ['http://www.swelluk.com']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//ul[@id="secnav"]/li/a/@href').extract()
        for category in categories:
            yield Request(category, callback=self.parse_categories)

    def parse_categories(self, response):
        hxs = HtmlXPathSelector(response)
        sub_categories =  hxs.select('//ul[@id="secnav"]/li/ul/li/a/@href').extract()
        for sub_category in sub_categories:
            yield Request(sub_category, callback=self.parse_products, meta={'do_pagination':True})

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//ul[@class="productList"]/li')
        for product in products:
            url = product.select('a/@href').extract()[0]
            price = product.select('div[@class="desc"]/strong/text()').extract()[0]
            if 'From' in price:
                yield Request(url, callback=self.parse_product)
            else:
                loader = ProductLoader(item=Product(), selector=product)   
                loader.add_xpath('name', 'div[@class="desc"]/h3/a/text()')
                loader.add_value('url', url)
                loader.add_value('price', price)
                yield loader.load_item()
        pages = hxs.select('//ul[@id="prod_page"][1]/li/a/@href').extract()
        if pages:
            if response.meta['do_pagination']:
                for page_url in pages:
                    yield Request(page_url, callback=self.parse_products, meta={'do_pagination':False})

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//tr[@style="background: #FAFAFA; border-bottom: 1px dotted #CCC;"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            name =  product.select('td/span[@class="prod_big"]/text()')[0].extract()
            loader.add_value('name', name)
            loader.add_value('url', response.url)
            price = product.select('td[@class="aligncentre"]/span[@class="prod_big"]/text()')[0].extract()
            loader.add_value('price', price)
            yield loader.load_item()
