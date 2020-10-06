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

class BlivakkerSpider(BaseSpider):
    name = 'blivakker.no'
    allowed_domains = ['blivakker.no']
    start_urls = ['http://www.blivakker.no']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//*[@id="mainNav"]/div[@class="mainNavElement"]/a[@href!="/"]/@href').extract()
        for category in categories:
            url =  urljoin_rfc(get_base_url(response), category)
            yield Request(url, callback=self.parse_subcategories)

    def parse_subcategories(self, response):
        hxs = HtmlXPathSelector(response)
        sub_categories = hxs.select('//*[@id="contentWrapper"]/div/div[@class="categoryElement"]/a/@href').extract()
        for sub_category in sub_categories:
            url =  urljoin_rfc(get_base_url(response), sub_category)
            yield Request(url, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products =  hxs.select('//*[@id="contentWrapper"]/div/div[@class="productElement"]')
        if products:
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)   
                loader.add_value('sku', ''.join(product.select('h2/a/@href').extract()).split('/')[-2])
                loader.add_xpath('name', 'h2/a/text()')
                url =  urljoin_rfc(get_base_url(response), ''.join(product.select('h2/a/@href').extract()))
                loader.add_value('url', url)
                price = ''.join(product.select('div[@class="productElementPrice"]/text()').extract()).strip().replace(u'\xa0','')
                loader.add_value('price', price.replace(',','.'))
                yield loader.load_item()
            next = hxs.select('//a[@class="nextprevSC" and text()=" Neste side"]/@href').extract()
            if next:
                url =  urljoin_rfc(get_base_url(response), next[0])
                yield Request(url, callback=self.parse_products)
        sub_categories = hxs.select('//*[@id="contentWrapper"]/div/div[@class="categoryElement"]/a/@href').extract()
        if sub_categories:
            yield Request(response.url, callback=self.parse_subcategories, dont_filter=True)
