from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader

from scrapy import log


class BisonPartsSpider(BaseSpider):
    name = 'bisonparts.co.uk'
    allowed_domains = ['www.bisonparts.co.uk']
    start_urls = ('http://www.bisonparts.co.uk',)

    def __init__(self, *args, **kwargs):
        super(BisonPartsSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # brands
        brands = hxs.select('//div[@id="trucks"]//a/@href').extract()
        for category in brands:
            url = urljoin_rfc(get_base_url(response), category)
            yield Request(url)

        # categories
        categories = hxs.select('//div[@id="categories"]//a/@href').extract()
        for category in categories:
            url = urljoin_rfc(get_base_url(response), category)
            yield Request(url)

        # pages
        next_page = hxs.select('//ul[contains(@class, "pagination")]/li/a[contains(text(), "Next")]/@href').extract()
        if next_page:
            url = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(url)

        products = hxs.select(u'//div[contains(@class,"products_content")]/ul/li/h4/a/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)

        # products
#        products = hxs.select(u'//div[contains(@class,"products_content")]/ul/li/h4/a/@href').extract()
#        for url in products:
#            url = urljoin_rfc(get_base_url(response), url)
#            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        # products
        products = hxs.select(u'//form/div[@id="price"]')

        if not products:
            product_loader = ProductLoader(item=Product(), response=response)
            product_loader.add_value('url', response.url)
            product_loader.add_xpath('name', u'//div[@class="product"]/h1/text()')
            price = hxs.select(u'//div[@class="product"]//p[@class="price1"]/text()').re(u'\xa3(.*)')
            if not price:
                return
            product_loader.add_value('price', price)
            yield product_loader.load_item()
        else:
            for product in products:
                product_loader = ProductLoader(item=Product(), selector=product)
                product_loader.add_xpath('name', u'./h4/text()')
                product_loader.add_value('url', response.url)
                price = product.select(u'.//p[@class="price1"]/text()').re('\xa3(.*[0-9])')
                if not price:
                    continue
                product_loader.add_value('price', price)
                yield product_loader.load_item()