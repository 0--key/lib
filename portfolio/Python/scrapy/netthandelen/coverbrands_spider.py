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

class CoverBrandsSpider(BaseSpider):
    name = 'coverbrands.no'
    allowed_domains = ['coverbrands.no']
    start_urls = ['http://www.coverbrands.no/shop/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//ul[@class="leftMenu"]/li/a/@href').extract()
        for category in categories:
            url =  urljoin_rfc(get_base_url(response), category)
            yield Request(url, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//li[@class="product" or @class="product end"]')
        for product in products:
            name = ''.join(product.select('div/div[@class="heading"]/h2/text()').extract())
            if name:
                loader = ProductLoader(item=Product(), selector=product)
                brand = ''.join(product.select('div/div[@class="heading"]/h3/text()').extract())
                loader.add_value('name', ' '.join((brand, name)))
                relative_url =  product.select('div/a[@class="productOverlay"]/@href').extract()
                loader.add_value('url', urljoin_rfc(get_base_url(response), relative_url[0]))
                price = ''.join(product.select('div/p[@class="price color"]/text()').extract()).replace('.', '').replace(',', '.').replace(u'\xa0', '')
                if not price:
                    price = ''.join(product.select('div/p[@class="price "]/text()').extract()).replace('.', '').replace(',', '.').replace(u'\xa0', '')
                loader.add_value('price', price)
                yield loader.load_item()
        next = product.select('//div[@class="pageNavigation"]/ul/li[@class="next"]/a/@href').extract()
        if next:
            url =  urljoin_rfc(get_base_url(response), next[-1])
            yield Request(url, callback=self.parse_products)
