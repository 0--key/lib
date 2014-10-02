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

class BhphotoVideoSpider(BaseSpider):
    name = 'bhphotovideo.com'
    allowed_domains = ['bhphotovideo.com']
    start_urls = ['http://www.bhphotovideo.com/c/browse/SiteMap/ci/13296/N/4294590034']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//*[@id="tContent"]/div/div/div[@class="column"]/ul/li/a/@href').extract()
        for category in categories:
            yield Request(category, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="productBlock clearfix " or @class="productBlock clearfix topmrgn"]')
        if products:
            for product in products: 
                loader = ProductLoader(item=Product(), selector=product)
                brand = product.select('div/div/div[@class="brandTop"]/text()').extract()[0]
                title = product.select('div/div[@id="productTitle"]/h2/a/text()').extract()[0]
                name = ' '.join((brand, title))
                loader.add_value('name', name)
                price = product.select('div[@id="productRight"]/ul/li[@class="price"]/span[@class="value"]/text()').extract()
                if price:
                    price = price[0]
                else:
                    price = product.select('div[@id="productRight"]/ul/li[@class="discountPrice"]/span[@class="value"]/text()').extract()
                    if price:
                        price = price[0]
                    else:
                        price = product.select('div[@id="productRight"]/ul/li[@class="map youPay"]/span[@class="value"]/text()').extract()
                        if price:
                            price = price[0]
                        else:
                            price = product.select('div/ul/li/span[@class="value"]/text()').extract()
                            if price:
                                price = price[0]
                            else:
                                price = ''
                loader.add_xpath('url', 'div/div[@id="productTitle"]/h2/a/@href')
                loader.add_value('price', price)
                yield loader.load_item()
        next = hxs.select('//*[@id="bottompagination"]/div/a[@class="lnext"]/@href').extract()
        if next:
            if len(next)>1:
                yield Request(next[1], callback=self.parse_products)
            else:
                yield Request(next[0], callback=self.parse_products)
        else:
            yield Request(response.url, dont_filter=True)


