import os
import shutil
from scrapy import signals
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url
from scrapy.xlib.pydispatch import dispatcher

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class PlumbtradersSpider(BaseSpider):
    name = 'plumbtraders.co.uk'
    allowed_domains = ['plumbtraders.co.uk']
    start_urls = ['http://www.plumbtraders.co.uk/sitemap/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//div[@class="sub-menu"]/ul/li/dl/dt/a/@href').extract()
        if categories:
            for category in categories:
                url =  urljoin_rfc(get_base_url(response), category)
                yield Request(url+'?page=all', callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="product"]')
        if products:
            for product in products:
                #loader = ProductLoader(item=Product(), selector=product)
                #loader.add_xpath('name', 'h2[@class="product-name"]/a/text()')
                relative_url = ''.join(product.select('h2[@class="product-name"]/a/@href').extract())
                name = ''.join(product.select('h2[@class="product-name"]/a/text()').extract())
                url = urljoin_rfc(get_base_url(response), relative_url)
                #loader.add_value('url', url)
                #loader.add_xpath('price', 'div[@class="product-price"]/p/text()')
                yield Request(url, callback=self.parse_product, meta={'name':name})#loader.load_item()
        else:
            categories = hxs.select('//*[@id="category-list"]/div[@class="row"]/div[@class="span3"]/div/div/h2/a/@href').extract()
            if categories:
                for category in categories:
                    url =  urljoin_rfc(get_base_url(response), category)
                    yield Request(url+'?page=all', callback=self.parse_products)   

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        loader = ProductLoader(item=Product(), response=response)
        mpn = ''.join(hxs.select('//*[@id="product-information"]/table/tr[th/text()="Part number"]/td/span/text()').extract()).strip()
        loader.add_value('identifier', mpn)
        loader.add_value('name', ' '.join((response.meta['name'].strip(), mpn)))
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//*[@id="product-price"]/p[@class="no-vat"]/text()')
        yield loader.load_item()
