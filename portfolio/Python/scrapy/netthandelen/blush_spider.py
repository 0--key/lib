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

class BlushSpider(BaseSpider):
    name = 'blush.no'
    allowed_domains = ['blush.no']
    start_urls = ['https://www.blush.no/default.aspx']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//div[@class="topmenucenter"]/div/a[not(@id="hjematag")]/@href').extract()
        for category in categories:
            url =  urljoin_rfc(get_base_url(response), category)
            yield Request(url, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div/div/table')
        for product in products:
            name = ''.join(product.select('tr/td/div[@class="featuredProductLinks"]/a/text()').extract())
            if name:
                loader = ProductLoader(item=Product(), selector=product)
                brand = ''.join(product.select('tr/td/div[@class="featuredMIS"]/a/text()').extract())
                loader.add_value('name', ' '.join((brand, name)))
                relative_url =  product.select('tr/td/div[@class="featuredProductLinks"]/a/@href').extract()
                loader.add_value('url', urljoin_rfc(get_base_url(response), relative_url[0]))
                price = ''.join(product.select('tr/td/div/div'
                                               '[@class="featuredProductPrice"]'
                                               '/span/span[@class="SalePrice1"]'
                                               '/text()').extract()).replace('.','').replace(',','.')
                if not price:
                    price = ''.join(product.select('tr/td/div/div'
                                                   '[@class="featuredProductPrice"]'
                                                   '/span/span[@class="variantprice1"]'
                                                   '/text()').extract()).replace('.','').replace(',','.')
                loader.add_value('price', price)
                yield loader.load_item()
        next = hxs.select('//div[@class="pagingdiv"]/a[not(@class)]/@href').extract()
        if next:
            url =  urljoin_rfc(get_base_url(response), next[-1])
            yield Request(url, callback=self.parse_products)
