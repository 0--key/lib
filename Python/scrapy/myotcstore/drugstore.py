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

class DrugstoreSpider(BaseSpider):
    name = 'drugstore.com'
    allowed_domains = ['www.drugstore.com', 'drugstore.com']
    start_urls = ('http://drugstore.com/',)

    def __init__(self, *args, **kwargs):
        super(DrugstoreSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//div[@id="MenuCntr"]//ul/li/a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # see all brands
        see_all = hxs.select(u'//a[contains(text(),"see all brands")]/@href').extract()
        if see_all:
            see_all = urljoin_rfc(get_base_url(response), see_all[0])
            yield Request(see_all)

        # price range
        price_range = hxs.select(u'//div[@class="srchRefine"]//a[preceding-sibling::div[@class="dimension" and text()="price range"]]/@href').extract()
        for price in price_range:
            price = urljoin_rfc(get_base_url(response), price)
            yield Request(price, callback=self.parse_product)
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        # pages
        next_page = hxs.select(u'//div[@style="float:left;padding-right:8px;"]/a[child::img]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page, callback=self.parse_product)

        products = hxs.select(u'//div[contains(@class,"itemGrid")]')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//a[@class="oesLink"]/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)
            name = product.select(u'.//a[@class="oesLink"]/span/text()').extract()[0]
            name += ' ' + product.select(u'.//a[@class="oesLink"]/text()').extract()[0]
            product_loader.add_value('name', name)
            product_loader.add_xpath('price', u'.//span[@class="PlistOfferPrice"]/text()',
                                 re=u'\$(.*)')
            product_loader.add_xpath('price', u'.//div[@class="pricing"]/span/div/span/text()',
                                 re=u'\$(.*)')
            loaded = product_loader.get_output_value('name') and product_loader.get_output_value('price')
            if not loaded:
                continue
            yield product_loader.load_item()