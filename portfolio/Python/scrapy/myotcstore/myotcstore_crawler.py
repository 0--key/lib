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
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class MyOTCStoreSpider(BaseSpider):
    name = 'myotcstore.com'
    allowed_domains = ['www.myotcstore.com', 'myotcstore.com']
    start_urls = ('http://www.myotcstore.com/',)

    def __init__(self, *args, **kwargs):
        super(MyOTCStoreSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select('//div[@id="atoz"]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)


        # subcategories
        subcategories = hxs.select(u'//div[@class="CategoryChildCategoriesLink"]/a/@href').extract()
        subcategories += hxs.select('//div[@id="relatedbrands"]//a/@href').extract()
        for url in subcategories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pagination
        next_page = hxs.select(u'//div[@class="CategoryPageNavigation"]//a[child::span[contains(text(),"Next")]]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        # products
        for product in self.parse_product(response):
            yield product
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)


        products = hxs.select(u'//div[@id="divProductRow"]')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//span[@class="CategoryProductNameLink"]/a/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)
            product_loader.add_xpath('name', u'.//span[@class="CategoryProductNameLink"]/a/text()')
            product_loader.add_xpath('price', u'.//span[@id="lblSalePrice"]/text()',
                                     re=u'\$(.*)')
            product_loader.add_xpath('price', u'.//span[@id="lblPrice"]/text()',
                                     re=u'\$(.*)')
            # loaded = (product_loader.get_output_value('name')) and (product_loader.get_output_value('price'))
            # if loaded:
            yield product_loader.load_item()