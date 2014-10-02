#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Version 0.01
#       Started 12.08.2012
#       Autor   Roman <romis@wippies.fi>
from scrapy.http import Request
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoader

class Paddockfarm(BaseSpider):
    name = 'paddockfarm'
    allowed_domains = ['paddockfarm.co.uk']
    start_urls = ['http://www.paddockfarm.co.uk']
    
    def parse(self, response): 
        hxs = HtmlXPathSelector(response)
        urls = [urljoin_rfc(get_base_url(response), x.strip()) for x in hxs.select(".//*[@class='leftnavlist']/li/a/@href").extract() if x.strip()]
        for url in urls:
            yield Request(url, callback=self.parse_listing_page)


    def parse_listing_page(self, response):
        hxs = HtmlXPathSelector(response)
        url = response.url
        prod_box = hxs.select(".//*[@class='prodbox']")
        for product in  prod_box:
            loader = ProductLoader(item=Product(), selector=product)
            name = ''.join(product.select(".//div[@class='prodtitle']/.//a/text()").extract())
            price = ''.join(product.select(".//div[@class='prodprice']/strong/.//text()").extract())
            loader.add_value('name', name)
            loader.add_value('url', url)
            loader.add_value('price', price)
            yield loader.load_item() 
            
        next_page = hxs.select(".//a[contains(text(), 'Next')]/@href")
        if next_page:
            next_url = urljoin_rfc(get_base_url(response), next_page[0].extract())
            yield Request(next_url, callback=self.parse_listing_page)

