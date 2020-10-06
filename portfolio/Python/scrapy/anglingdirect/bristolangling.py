import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader


class BristolAnglingSpider(BaseSpider):
    name = 'bristolangling.com'
    allowed_domains = ['www.bristolangling.com']
    start_urls = ('http://www.bristolangling.com/',)

    def __init__(self, *args, **kwargs):
        super(BristolAnglingSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//ul[@id="nav"]/li/a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pages
        next_page = hxs.select(u'//a[@class="next i-next"]/@href').extract()
        if next_page:
            url = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(url)

        # products
        products = hxs.select(u'//h2[@class="product-name"]/a/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        name = hxs.select(u'//div[@class="product-name fn"]/h1/text()').extract()[0]

        multiple_prices = hxs.select(u'//table[@id="super-product-table"]//tr')
        if not multiple_prices:
            product_loader = ProductLoader(item=Product(), response=response)
            product_loader.add_value('name', name)
            product_loader.add_value('url', response.url)
            product_loader.add_xpath('price', u'//div[@class="price-box"]/span[contains(@id,"product-price")]/span[@class="price"]/text()',
                                     re='\xa3(.*[0-9])')
            product_loader.add_xpath('price', u'//div[@class="price-box"]/p[@class="special-price"]/span[@class="price"]/text()',
                                     re='\xa3(.*[0-9])')
            yield product_loader.load_item()
        else:
            for name_and_price in multiple_prices:
                product_loader = ProductLoader(item=Product(), selector=name_and_price)
                name_options = name_and_price.select(u'./td[position()=1]/text()').extract()[0]
                product_loader.add_value('name', name + ' ' + name_options)
                product_loader.add_value('url', response.url)
                product_loader.add_xpath('price', u'./td[position()=2]/div[@class="price-box"]/span[@class="regular-price"]/span[@class="price"]/text()',
                                         re=u'\xa3(.*)')
                product_loader.add_xpath('price', u'./td[position()=2]/div[@class="price-box"]/p[@class="special-price"]/span[@class="price"]/text()',
                                         re=u'\xa3(.*)')
                yield product_loader.load_item()