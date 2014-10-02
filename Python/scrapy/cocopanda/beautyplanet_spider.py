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

class BeautyPlanetSpider(BaseSpider):
    name = 'cocopanda-beautyplanet.no'
    allowed_domains = ['beautyplanet.no']
    start_urls = ['http://www.beautyplanet.no/Kvinne/Varemerke.aspx',
                  'http://www.beautyplanet.no/Mann/Varemerke.aspx']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        brands = hxs.select('//div[@class="Mod5ColBody"]/table/tr/td/div/a/@href').extract()
        for brand in brands:
            url =  urljoin_rfc(get_base_url(response), brand)
            yield Request(url, callback=self.parse_categories)

    def parse_categories(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//*[@id="PageMenu"]/div/a/@href').extract()
        for category in categories:
            url =  urljoin_rfc(get_base_url(response), category)
            yield Request(url, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="ProductDisplay"]/div[@class="Info"]')
        for product in products:
            name = ''.join(product.select('div/h1/a/text()').extract())
            if name:
                loader = ProductLoader(item=Product(), selector=product)
                brand = ''.join( product.select('div/h4/a/text()').extract())
                loader.add_value('name', ' '.join((brand, name)))
                relative_url =  product.select('div/h1/a/@href').extract()
                loader.add_value('url', urljoin_rfc(get_base_url(response), relative_url[0]))
                price = ''.join(product.select('h3/span[@class="Price"]/text()').extract()).replace('.','').replace(',','.')
                #if not price:
                #    price = ''.join(product.select('tr/td/div/div'
                #                                   '[@class="featuredProductPrice"]'
                #                                   '/span/span[@class="variantprice1"]'
                #                                   '/text()').extract()).replace('.','').replace(',','.')
                loader.add_value('price', price)
                yield loader.load_item()
        #next = hxs.select('//div[@class="pagingdiv"]/a[not(@class)]/@href').extract()
        #if next:
        #    url =  urljoin_rfc(get_base_url(response), next[-1])
        #    yield Request(url, callback=self.parse_products)
