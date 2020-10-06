import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader


class FostersOfBirminghamSpider(BaseSpider):
    name = 'fostersofbirmingham.co.uk'
    allowed_domains = ['www.fostersofbirmingham.co.uk']
    start_urls = ('http://www.fostersofbirmingham.co.uk/',)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//ul[@id="pinNav" and @class="lv1"]/li/a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pages
        next_page = hxs.select(u'//span[@class="pg"]//span[@class="n"]//a/@href').extract()
        if next_page:
            url = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(url)

        # products
        products = hxs.select(u'//h3[@class="ti"]/a/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        multiple_prices = hxs.select(u'//table[@class="grpChld"]//tr[@class="r1"]')
        if not multiple_prices:
            product_loader = ProductLoader(item=Product(), response=response)
            product_loader.add_xpath('name', u'//div[@class="det"]/h1/text()')
            product_loader.add_value('url', response.url)
            product_loader.add_xpath('price', u'//div[@class="addBsk"]/div[@class="pri"]/b/text()',
                                     re=u'\xa3(.*)')
            yield product_loader.load_item()
        else:
            for name_and_price in multiple_prices:
                product_loader = ProductLoader(item=Product(), selector=name_and_price)
                product_loader.add_xpath('name', u'./td[@class="c1"]/text()',
                                         re=u'.*?-[\xa0]*(.*)')
                product_loader.add_value('url', response.url)
                product_loader.add_xpath('price', u'./following-sibling::node()[1]/td[@class="c3"]/span/text()',
                                         re=u'\xa3(.*)')
                yield product_loader.load_item()
