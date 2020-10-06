import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode

import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class VitaCostSpider(BaseSpider):
    name = 'vitacost.com'
    allowed_domains = ['www.vitacost.com', 'vitacost.com']
    start_urls = ('http://vitacost.com/Brands',)

    def __init__(self, *args, **kwargs):
        super(VitaCostSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # brands
        brands = hxs.select(u'//ul[@class="linkList4"]//li//a/@href').extract()
        for url in brands:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pages
        next_page = hxs.select(u'//a[text()="next>"]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        for product in self.parse_product(response):
            yield product
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)
        products = hxs.select(u'//div[@class="pt9P cf clear"]')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//a[@class="pNameM cf"]/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)
            product_loader.add_xpath('name', u'.//a[@class="pNameM cf"]/text()')
            product_loader.add_xpath('price', u'.//div[contains(@class,"pOurPrice")]/text()',
                                 re=u'\$(.*)')
            if product_loader.get_output_value('price'):
                yield product_loader.load_item()
            else:
                cart_url = product.select(u'.//div[@class="pt0PBtns"]/a[child::img]/@href').extract()[0]
                cart_url = urljoin_rfc(get_base_url(response), cart_url)
                request = Request(cart_url, callback=self.parse_cart, cookies={}, meta={'dont_merge_cookies': True})
                request.meta['product_loader'] = product_loader
                yield request

    def parse_cart(self, response):
        hxs = HtmlXPathSelector(response)

        product = hxs.select('//tr[child::td[@class="pNameM"]]').extract()[0]

        product_loader = response.meta['product_loader']
        name = product.select('.//td[@class="pNameM"]/a/text()').extract()[0]
        if name == product_loader.get_output_value('name'):
            price = product.select('.//td[@class="scPrice"]/text()').re(u'\$(.*)')[0]
            product_loader.add_value('price', price)
            yield product_loader.load_item()
        else:
            yield product_loader.load_item()