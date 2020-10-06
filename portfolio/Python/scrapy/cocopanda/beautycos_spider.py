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

class BeautycosSpider(BaseSpider):
    name = 'cocopanda-beautycos.dk'
    allowed_domains = ['beautycos.dk']
    start_urls = ['http://www.beautycos.dk']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//form/select/option/@value').extract()
        for category in categories:
            yield Request('http://www.beautycos.dk/group.asp?group='+category, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products =  hxs.select('//table[@class="group-list"]/tr/td/table/tr/td[@id="group"]')
        if products:
            for product in products:
                url =  urljoin_rfc(get_base_url(response), ''.join(product.select('font/a[1]/@href').extract()))
                price = ''.join(product.select('font/b/text()').extract()).replace('.','').replace(',','.')
                if 'Pris' not in price:# == 'Midlertidig udsolgt':
                    yield Request(url, callback=self.parse_product)
                else:
                    loader = ProductLoader(item=Product(), selector=product)   
                    loader.add_xpath('name', 'font/a/text()')
                    loader.add_value('url', url)
                    loader.add_value('price', price)
                    yield loader.load_item()

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        loader = ProductLoader(item=Product(), response=response)
        loader.add_xpath('name', '//*[@id="header"]/text()')
        loader.add_value('url', response.url)
        price = ''.join(hxs.select('//*[@id="productdesc"]/font/font/text()').extract()).replace('.','').replace(',','.')
        if price:
            price = price.split(':')[-1]
        loader.add_value('price', price)
        yield loader.load_item()
