import re

from decimal import Decimal

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product

class TyreDriveCoUk(BaseSpider):
    name = 'tyredrive.co.uk'
    allowed_domains = ['tyredrive.co.uk', 'www.tyredrive.co.uk']
    start_urls = ('http://www.tyredrive.co.uk',)

    def __init__(self, *args, **kwargs):
        super(TyreDriveCoUk, self).__init__(*args, **kwargs)
        self.URL_BASE = 'http://www.tyredrive.co.uk'

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        
        hxs = HtmlXPathSelector(response)

        try:
            product = {}
            name = hxs.select('//h1[following-sibling::span]/text()').extract()[0]
            url = response.url
            price = hxs.select('//table[@class="searchresults" and position()=1]//td[@class="netprice"]') \
                       .re('\xa3(.*)<')[0]
            price = Decimal(price) + Decimal(3)
            price = str(price)
            product['url'] = url
            product['description'] = name
            product['price'] = price
            yield load_product(product, response)
        except IndexError:
            return


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        # categories and subcategories
        category_urls = hxs.select('//li[translate(@class,"0123456789","")="col"]/a/@href').extract()
        for url in category_urls:
            url = urljoin_rfc(self.URL_BASE, url)
            yield Request(url)


        # next page
        # next_page = 
        # if next_page:
        #     url = urljoin_rfc(URL_BASE, next_page[0])
        #   yield Request(url)

        # products
        products = hxs.select('//table[@class="searchresults"]//a/@href').extract()
        for url in products:
            url = urljoin_rfc(self.URL_BASE, url)
            yield Request(url, callback=self.parse_product)
