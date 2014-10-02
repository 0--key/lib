#!/usr/bin/python
# -*- coding: latin-1 -*-

import logging

from scrapy import log
from scrapy.http import Request
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class PixmaniaSpider(BaseSpider):
    name = "pixmania.com_tec7"
    allowed_domains = ["pixmania.com"]
    start_urls = (
        'http://www.pixmania.co.uk/uk/uk/cameras/digital-camera/1/1/categorie.html',
        'http://www.pixmania.co.uk/uk/uk/tv-video/television/8/3/categorie.html'
    )

    page_suffix = "?sPageInfo=%page%_50"

    def parse(self, response):
        base_url = response.url

        hxs = HtmlXPathSelector(response)

        count = hxs.select("//div[@class='search-title']/span[@class='search-result']/text()").re('(\d*) products match your search')
        if not count:
            logging.error("Products count not found!")
            return
        count = count[0]

        for page in range(1, (int(count) / 50) + 3):
            url = base_url + self.page_suffix.replace("%page%", str(page))
            yield Request(url=url, callback=self.parse_products, dont_filter=True)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select("//div[@class='box-caracteristic-search']/div[@class='table-wrap']/form/table/tbody/tr")
        for product in products:
            name = product.select("td[@class='prd-details']/h3/a/text()").extract()
            if not name:
                logging.error("ERROR! No name! %s" % response.url)
                continue
            name = name[0]

            url = product.select("td[@class='prd-details']/h3/a/@href").extract()
            if not url:
                logging.error("ERROR! NOT FOUND URL! URL: %s. NAME: %s" % (response.url, name))
                continue
            url = url[0]
            url = self._urljoin(response, url)

            price = product.select("td[@class='prd-amount-details']/div/p[@class='prd-amount']/strong/text()").extract()
            if not price:
                logging.error("ERROR! NOT FOUND PRICE! URL: %s. NAME: %s" % (response.url, name))
                continue
            price = price[0]

            l = ProductLoader(item=Product(), response=response)
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()

    def _urljoin(self, response, url):
        """Helper to convert relative urls to absolute"""
        return urljoin_rfc(response.url, url, response.encoding)

    def _encode_price(self, price):
        return price.replace(',','.').encode("ascii","ignore")
