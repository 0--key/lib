import re
import os
from urlparse import urlparse

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader


class TedCarterSpider(BaseSpider):
    name = 'tedcarter.co.uk'
    allowed_domains = ['www.tedcarter.co.uk']
    start_urls = ('http://www.tedcarter.co.uk/',)

    def __init__(self, *args, **kwargs):
        super(TedCarterSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//li[@class="mega "]/span/a/@href').extract()
        for url in categories:
            parsed_url = urlparse(url)
            url = urljoin_rfc(get_base_url(response), url)
            url += '&perPage=20'
            yield Request(url)

        # pages
        last_page = hxs.select(u'//div[@class="pages"]/span/a/text()').extract()
        url_parts = response.url.split('&')
        if last_page: # make requests only from page 1
            last_page = int(last_page[-1])
            for i in xrange(2, last_page + 1):
                url = url_parts[0] + '&perPage=20&currentPage=' + str(i)
                yield Request(url)

        # products
        products = hxs.select(u'//div[@class="browse-product"]/a/@href').extract()

        for url in products:
            yield Request(url, callback=self.parse_product)


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        multiple_prices = hxs.select(u'//table[@class="product-qty-table"]/tr')
        if not multiple_prices:
            product_loader = ProductLoader(item=Product(), response=response)
            product_loader.add_xpath('name', u'//h1[@class="product-title"]/text()')
            product_loader.add_value('url', response.url)
            product_loader.add_xpath('price', u'//p[@class="now-table"]/text()', re=u'\xa3(.*)')
            yield product_loader.load_item()
        else:
            for name_and_price in multiple_prices:
                product_loader = ProductLoader(item=Product(), selector=name_and_price)
                name = hxs.select(u'//h1[@class="product-title"]/text()').extract()[0]
                name += ' ' + name_and_price.select(u'./td[position()=1]/text()').extract()[0]
                product_loader.add_value('name', name)
                product_loader.add_value('url', response.url)
                product_loader.add_xpath('price', u'./td[position()=2]/p[@class="now-table"]/text()',
                                         re=u'\xa3(.*)')
                yield product_loader.load_item()
