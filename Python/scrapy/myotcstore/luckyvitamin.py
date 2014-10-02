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

class LuckyVitaminSpider(BaseSpider):
    name = 'luckyvitamin.com'
    allowed_domains = ['www.luckyvitamin.com', 'luckyvitamin.com']
    start_urls = ('http://luckyvitamin.com/brands',)

    def __init__(self, *args, **kwargs):
        super(LuckyVitaminSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # brands
        brands = hxs.select(u'//ul[@class="alpha-categories"]//a/@href').extract()
        for url in brands:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pages
        next_page = hxs.select(u'//li[@class="pagingArrow"]/a/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        for product in self.parse_product(response):
            yield product
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)
        products = hxs.select(u'//ul[@class="product-list"]/li')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//div[@class="listItemLink"]/a/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)
            name = product.select(u'.//div[@class="listBrand"]/text()').extract()[0]
            name += ' ' + product.select(u'.//div[@class="listItemLink"]/a/text()').extract()[0]
            name += ' ' + product.select(u'.//div[@class="listData"]/text()').extract()[0]
            product_loader.add_value('name', name)
            product_loader.add_xpath('price', u'.//span[@class="salePrice"]/span/text()',
                                 re=u'\$(.*)')
            yield product_loader.load_item()