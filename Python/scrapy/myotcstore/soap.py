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

class SoapSpider(BaseSpider):
    name = 'soap.com'
    allowed_domains = ['www.soap.com', 'soap.com']
    start_urls = ('http://soap.com/',)

    def __init__(self, *args, **kwargs):
        super(SoapSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//a[@class="siteNavLink"]/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # categories
        categories = hxs.select(u'//ul[@id="categoryList"]/li/a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pages
        next_page = hxs.select(u'//a[child::span[@class="blueArrowRightBtn"]]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        products = hxs.select(u'//div[@class="show"]/ul/li//h1[@class="showName"]/a/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        multiple_products = hxs.select(u'//table[@class="productItemTable"]/tr[child::td[@class="itemImage"]]')

        for product in multiple_products:

            product_loader = ProductLoader(item=Product(), selector=product)
            product_loader.add_value('url', response.url)
            name = product.select(u'.//td[@align="left"]/text()').extract()[0]
            if len(name) < 8:
                name = hxs.select(u'//h1[contains(@class,"quickproductShowName")]/text()').extract()[0].strip() + ' ' + name
            product_loader.add_value('name', name)
            product_loader.add_xpath('price', u'.//span[@class="salePrice"]/text()',
                                             re=u'\$(.*)')
            product_loader.add_xpath('price', u'.//span[@class="normalPrice"]/text()',
                                 re=u'\$(.*)')
            yield product_loader.load_item()