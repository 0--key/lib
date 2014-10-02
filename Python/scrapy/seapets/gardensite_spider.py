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

class GardenSiteSpider(BaseSpider):
    name = 'gardensite.co.uk'
    allowed_domains = ['gardensite.co.uk']
    start_urls = ['http://www.gardensite.co.uk/Aquatics/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//ul[@class="side_menu_group"]/li/a/@href').extract()
        for category in categories:
            url =  urljoin_rfc(get_base_url(response), category)
            yield Request(url, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="contentb" and descendant::'
                              'div[@class="product_cell_price_thumb" or '
                              '@class="product_cell_price_double" or '
                              '@class="product_cell_price_long"]/div[@style="float:right;"]]')
        if products:
            for product in products:
                relative_url = ''.join(product.select('div/div[@class="product_cell_thumb_title"]/a/@href').extract())
                if not relative_url:
                    relative_url = ''.join(product.select('div[@class="product_cell_double_title"]/a/@href').extract())
                    if not relative_url:
                        relative_url = ''.join(product.select('div/div[@class="product_cell_long_title"]/a/@href').extract())
                    
                price = ''.join(product.select('div[@class="product_cell_price_thumb"]'
                                               '/div[@style="float:right;"]/'
                                               'span[@class="new_price"]/text()').extract())
                if not price:
                    price = ''.join(product.select('div[@class="product_cell_price_double"]'
                                                   '/div[@style="float:right;"]/'
                                                   'span[@class="new_price"]/text()').extract())
                    if not price:
                        price = ''.join(product.select('div[@class="product_cell_price_long"]'
                                                   '/div[@style="float:right;"]/'
                                                   'span[@class="new_price"]/text()').extract())
                if 'FROM' in price:
                    yield Request(urljoin_rfc(get_base_url(response), relative_url), callback=self.parse_details)
                else:
                    loader = ProductLoader(item=Product(), selector=product)
                    name = ''.join(product.select('div/div[@class="product_cell_thumb_title"]/a/text()').extract())
                    if not name:
                        name = ''.join(product.select('div[@class="product_cell_double_title"]/a/text()').extract())
                        if not name:
                            name = ''.join(product.select('div/div[@class="product_cell_long_title"]/a/text()').extract())
                    loader.add_value('name', name)
                    loader.add_value('url', urljoin_rfc(get_base_url(response), relative_url))
                    loader.add_value('price', price)
                    yield loader.load_item()
            detailed_products = hxs.select('//div[@class="contentb"]/div[@class="product_cell_price_thumb"]/a[@class="new_price"]/@href').extract()
            for detail_product in detailed_products:
                url =  urljoin_rfc(get_base_url(response), detail_product)
                yield Request(url, callback=self.parse_details)
        else:
            yield Request(response.url, dont_filter=True)

    def parse_details(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="group_cell"]/div[@class="contentb"]/table/tr/td/div/div')
        if not products:
            products = hxs.select('//div[@class="group_cell"]/div')
        for product in products:
            price = ''.join(product.select('div[@class="complex_price"]/text()').extract()).strip()
            name = ''.join(product.select('div[@class="complex_title"]/text()').extract()).strip()
            if price:
                loader = ProductLoader(item=Product(), selector=product)
                loader.add_value('name', name)
                loader.add_value('url', response.url)
                loader.add_xpath('price', 'div[@class="complex_price"]/text()')
                yield loader.load_item()
        
