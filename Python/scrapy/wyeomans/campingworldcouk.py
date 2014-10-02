# -*- coding: utf-8 -*-
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

import logging

class CampingworldCoUkSpider(BaseSpider):
    name = 'campingworld.co.uk'
    allowed_domains = ['campingworld.co.uk']
    start_urls = (
        'http://www.campingworld.co.uk/',
        )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        categories = hxs.select("//td[@class='LeftNavHeader']/table[@class='Table5']/tr/td/a/@href").extract()
        for url in categories:
            yield Request(urljoin_rfc(base_url, url), callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        items = hxs.select("//table[@id='ProductDataList']/tr/td[div[contains(@id, 'ModelLinkCell')]]")
        for item in items:
            name = item.select(".//a[contains(@id, 'ModelLink')]//text()").extract()
            if not name:
                logging.error("ERROR! NO NAME! %s" % response.url)
                return
            name = "".join(name)

            url = item.select(".//a[contains(@id, 'ModelLink')]/@href").extract()
            if not url:
                logging.error("ERROR! NO URL! %s %s" % (name, response.url))
                return
            url = urljoin_rfc(base_url, url[0])

            price = item.select("div[contains(@id, 'ModelPrice')]//td[@class='Label11']/text()").re(u'\xa3(.*)')
            if not price:
                logging.error("ERROR! NO PRICE! %s %s" % (url, name))
                return
            price = price[0]

            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', name)
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()
