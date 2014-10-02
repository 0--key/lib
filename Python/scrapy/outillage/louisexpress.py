import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
import hashlib

import csv

from product_spiders.items import Product, ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class LouisExpressSpider(BaseSpider):
    name = 'louisexpress.com'
    allowed_domains = ['www.louisexpress.com', 'louisexpress.com']
    start_urls = ('http://www.louisexpress.com/shop/index.php?cPath=122&osCsid=g7qmemkgja03atanki359rt0tdha6qdp',
                  'http://www.louisexpress.com/shop/index.php?cPath=5&osCsid=g7qmemkgja03atanki359rt0tdha6qdp',
                  'http://www.louisexpress.com/shop/index.php?cPath=503&osCsid=g7qmemkgja03atanki359rt0tdha6qdp')

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        monitored_categories = [u'Bricolage', u'Technique de nettoyage', u'Outillage Jardin']
        for category in monitored_categories:
            category_urls = hxs.select(u'//div[@class="suckerdiv"]/ul[child::li[child::a[contains(text(),"%s")]]]//a/@href' % category).extract()
            for url in category_urls:
                url = urljoin_rfc(get_base_url(response), url)
                yield Request(url)

        # categories
        categories = hxs.select(u'//td[@class="smallText"]/a[child::br]/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pagination
        next_page = hxs.select(u'//a[child::u[contains(text(),"Suivante")]]/@href').extract()
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

        products = hxs.select(u'//tr[contains(@class,"productListing")]')
        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'./td[@class="productListing-data" and position()=3]/a/@href').extract()
            if not url:
                continue
            url = urljoin_rfc(get_base_url(response), url[0])
            product_loader.add_value('url', url)
            name = product.select(u'./td[@class="productListing-data" and position()=2]/a/text()').extract()[0]
            name += ' ' + product.select(u'./td[@class="productListing-data" and position()=3]/a/text()').extract()[0]
            product_loader.add_value('name', name)
            price = product.select(u'./td[@class="productListing-data" and position()=5]/span[@class="productSpecialPrice"]/text()').re(u'([\d\.,]+)')
            if not price:
                price = product.select(u'./td[@class="productListing-data" and position()=5]/text()').re(u'([\d\.,]+)')
            price = price[0]
            if '.' in price:
                price = price.replace('.', '')
            price = price.replace(',', '.')
            product_loader.add_value('price', price)
            yield product_loader.load_item()
