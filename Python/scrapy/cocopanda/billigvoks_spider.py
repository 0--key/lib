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

class BilligvoksSpider(BaseSpider):
    name = 'cocopanda-billigvoks.dk'
    allowed_domains = ['billigvoks.dk']
    start_urls = ['http://www.billigvoks.dk']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//td[@class="produkt_menu"]/div/table/tr/td/a/@href').extract()
        for category in categories:
            url =  urljoin_rfc(get_base_url(response), category)
            yield Request(url, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div/div[@style="width: 334px; height: 151px; float: left; padding: 3px;"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            name = product.select('div/div/script/text()').extract()[1].split("underline;\'>")[1].split('</a>")')[0]
            loader.add_value('name', name)
            relative_url =  product.select('div/div/script/text()').extract()[0].split("href='")[1].split("'><img")[0]
            loader.add_value('url', urljoin_rfc(get_base_url(response), relative_url))
            price = ''.join(product.select('div/div/span/text()').extract()).replace(',','.')
            loader.add_value('price', price)
            yield loader.load_item()
