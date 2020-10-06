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

class ShirleyAquaticsSpider(BaseSpider):
    name = 'shirleyaquatics.co.uk'
    allowed_domains = ['shirleyaquatics.co.uk']
    start_urls = ['http://www.shirleyaquatics.co.uk/products.cfm']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//div[@class="plItemInner"]/div/a/@href').extract()
        for category in categories:
            url =  urljoin_rfc(get_base_url(response), category)
            yield Request(url, callback=self.parse_products)
        next = hxs.select('//span[@class="pageLinksContainer"]/span[@class="linkItem plEnd"]/a/@href').extract()
        if next:
            url =  urljoin_rfc(get_base_url(response), next[-1])
            yield Request(url)
        

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="plItemInner" and descendant::div/div/a[@class="plItemPrice"]]')
        if products:
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)   
                loader.add_xpath('name', 'div/div[@class="plItemTitle"]/text()')
                relative_url = product.select('div[@class="plItemImage"]/a/@href').extract()[0]
                loader.add_value('url', urljoin_rfc(get_base_url(response), relative_url))
                #price = ''.join(product.select('div[@class="price"]/b/text()').extract()).replace('.','').replace(',','.')
                loader.add_xpath('price', 'div/div/div/a[@class="plItemPrice"]/text()')
                yield loader.load_item()
            next = hxs.select('//span[@class="pageLinksContainer"]/span[@class="linkItem plEnd"]/a/@href').extract()
            if next:
                url =  urljoin_rfc(get_base_url(response), next[-1])
                yield Request(url, callback=self.parse_products)
        else:
            #sub_categories = hxs.select('//div[@class="cats"]/center/a/@href').extract()
            #for sub_category in sub_categories:
            #    url =  urljoin_rfc(get_base_url(response), sub_category)
            yield Request(response.url, dont_filter=True)
