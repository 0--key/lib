# -*- coding: utf-8 -*-


from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.response import get_base_url
from scrapy.http import Request

from product_spiders.items import ProductLoader, Product

import urlparse

__author__ = 'Theophile R. <rotoudjimaye.theo@gmail.com>'


class PortusDigitalSpider(BaseSpider):
    name = "portusdigital-px.rtrk.co.uk"
    allowed_domains = ["portusdigital-px.rtrk.co.uk"]
    start_urls = ["http://portusdigital-px.rtrk.co.uk"]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        for href in hxs.select('//ul[@id="nav"]/li/a/@href').extract():
            yield Request(urlparse.urljoin(base_url, href) + "?limit=25", callback=self.load_products)

    def load_products(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        next = hxs.select('//div[@class="pager"]//a[@class="next i-next"]')
        if next:
            href = next.select("./@href").extract()[0]
            yield Request(urlparse.urljoin(base_url, href), callback=self.load_products)

        for product_box in hxs.select('//ol[@id="products-list"]/li'):
            product_loader = ProductLoader(item=Product(), selector=product_box)

            product_loader.add_xpath('name', './/h2[@class="product-name"]/a/text()')
            product_loader.add_xpath('url', './/h2[@class="product-name"]/a/@href')

            if product_box.select('.//p[@class="special-price"]'):
                product_loader.add_xpath('price', './/div[@class="price-box"]/p[@class="special-price"]/span[@class="price"]/text()')
            else:
                product_loader.add_xpath('price', './/div[@class="price-box"]//span[@class="regular-price"]/span[@class="price"]/text()')

            yield product_loader.load_item()