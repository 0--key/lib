import re
import json
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.utils import extract_price

HERE = os.path.dirname(os.path.abspath(__file__))

class TEquipmentSpider(BaseSpider):
    name = 'tequipment.net'
    allowed_domains = ['tequipment.net']

    def start_requests(self):
        with open(os.path.join(HERE, 'tequipmentcats')) as f:
            urls = f.read().split()
            for url in urls:
                yield Request(url)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        '''
        if response.url == self.start_urls[0]:
            cats = hxs.select('//font[@size="2.5"]/../@href').extract()
            for cat in cats:
                url = urljoin_rfc(get_base_url(response), cat)
                yield Request(url)
        '''

        subcats = hxs.select('//img[contains(@src, "orange-arrow.gif")]/../font/a/@href').extract()
        subcats += hxs.select('//table[@class="categorytable"]//td[@class="categorymodelcell"]//a/@href').extract()
        for subcat in subcats:
            yield Request(urljoin_rfc(get_base_url(response), subcat))

        '''
        price_list = hxs.select('//a[contains(text(), "Price List")]/@href').extract()
        if not price_list:
            price_list = hxs.select('//a[contains(@href, "PriceList")]/@href').extract()
        if price_list:
            yield Request(urljoin_rfc(get_base_url(response), price_list[0]))
        '''

        next_page = hxs.select('//a/b[contains(text(), "Next Page")]/../@href').extract()
        if next_page:
            yield Request(urljoin_rfc(get_base_url(response), next_page[0]))

        for product in self.parse_products(hxs, response):
            yield product

    def parse_products(self, hxs, response):
        products = hxs.select('//table[@class="pricelisttable"]' +
                              '//td[@class="pricelistcelltitle"]/../../tr')[1:]
        for product in products:
            loader = ProductLoader(selector=product, item=Product())
            price = product.select('.//img[contains(@src, "addtocart.gif")]' +
                                   '/../../..//span[@class="pricelistcelldatatext"]/text()').extract()
            if not price:
                continue

            loader.add_value('price', price[0])
            loader.add_xpath('name', './/td[@class="pricelistcelldata" and position()=2]/text()')
            url = response.url
            model_url = product.select('.//td[@class="pricelistcelldata" and position()=1]' +
                                       '//a/@href').extract()
            if model_url:
                url = urljoin_rfc(get_base_url(response), model_url[0])

            loader.add_value('url', url)
            yield loader.load_item()
