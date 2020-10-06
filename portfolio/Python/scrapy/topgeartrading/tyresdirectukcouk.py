import re

from decimal import Decimal

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

class TyresDirectCoUk(BaseSpider):
    name = 'tyresdirectukcouk'
    allowed_domains = ['tyresdirectuk.co.uk', 'www.tyresdirectuk.co.uk']
    start_urls = ('http://www.tyresdirectuk.co.uk/brands.php',)

    def __init__(self, *args, **kwargs):
        super(TyresDirectCoUk, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        # categories and subcategories
        category_urls = hxs.select('//div[@class="content"]/div[@class="brandbox"]//a/@href').extract()
        for url in category_urls:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)


        # next page
        # next_page = 
        # if next_page:
        #     url = urljoin_rfc(self.URL_BASE, next_page[0])
        #   yield Request(url)

        # products
        for product in self.parse_product(response):
            yield product

    def parse_product(self, response):

        hxs = HtmlXPathSelector(response)

        products = hxs.select('//div[@class="shopprods"]')
        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            product_loader.add_xpath('name', './/p/strong/a/text()')
            url = product.select('.//p/strong/a/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)
            price = product.select('.//span[@class="price"]/text()').extract()[0]
            price = Decimal(price) + Decimal(5)
            price = str(price)
            product_loader.add_value('price', price)
            yield product_loader.load_item()

