# -*- coding: utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.response import get_base_url
from scrapy.http import Request

import urlparse

from product_spiders.items import ProductLoader, Product

__author__ = 'Theophile R. <rotoudjimaye.theo@gmail.com>'

class Sound1Spider(BaseSpider):
    name = "sound1.com"
    allowed_domains = ["sound1.com"]
    start_urls = ["http://www.sound1.com/portal/asp/default.asp"]

    def parse(self, response):
        base_url = get_base_url(response)
        xhs = HtmlXPathSelector(response)

        cat_urls = set()
        for href in xhs.select("//a[@class='enkeltprodlink']/@href").extract():
            url = urlparse.urljoin(base_url, href)
            if url not in cat_urls:
                cat_urls.add(url)
                yield Request(url, callback=self.parse_category)
                
    def parse_category(self, response):
        base_url = get_base_url(response)
        xhs = HtmlXPathSelector(response)

        for href in xhs.select("//div[@id='produktmeny']//a/@href").extract():
            if href.startswith('javascript:'):
                url = urlparse.urljoin(base_url, href.split("'")[1])
                yield Request(url, callback=self.parse_product_listing)

    def parse_product_listing(self, response):
        xhs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        product_name_tr = None

        trows = xhs.select("//table[@class='lightyellowsmall']//table[@class='lightyellowsmall']/tr")

        for index, tr in enumerate(trows):
            if tr.select(".//a/strong"):
                product_name_tr = tr
                continue
            if tr.select(".//span[@class='blackpricelinebig']"):
                href = product_name_tr.select(".//a/@href").extract()[0]
                product_url = urlparse.urljoin(base_url, href)
                name = product_name_tr.select(".//a/strong/text()").extract()[0]
                price = tr.select(".//span[@class='blackpricelinebig']/text()").extract()[0].strip("NOK ")

                #if not product_url in self.unique_product_urls:
                product_loader = ProductLoader(item=Product(), response=response)
                product_loader.add_value('name', name)
                product_loader.add_value('url', urlparse.urljoin(base_url, href))
                product_loader.add_value('price', "".join(price.split()))

                product_name_tr = None

                yield product_loader.load_item()

