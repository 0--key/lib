#!/usr/bin/env python
# -*- coding: utf-8 -*#
#       Version 0.01
#       Started 27.07.2012
#       Autor   Roman 
from decimal import Decimal
from scrapy.http import Request
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from product_spiders.items import Product, ProductLoader

class CmcaquaticsSpider(BaseSpider):
    name = 'cmcaquatics'
    allowed_domains = ['cmcaquatics.co.uk']
    start_urls = ['http://www.cmcaquatics.co.uk/dynamic_sitemap.php']

    def parse(self, response): 
        hxs = HtmlXPathSelector(response)
        urls = [x.strip() for x in hxs.select(".//td[1]/ul[@class='sitemap']\
                /.//li/a/@href").extract() if x.strip()]
        for url in set(urls):
            yield Request(url, callback=self.parse_listing_page)


    def parse_listing_page(self, response):
        hxs = HtmlXPathSelector(response)
        product_urls = [x for x in hxs.select(".//*[@class='productlistingBox']\
                        /.//h2/a/@href").extract() if x]
        if product_urls:
            for product_url in product_urls:
                yield Request(product_url, callback=self.parse_product_page)
                
            next_page = hxs.select(".//a[@class='pageResults' and\
                                    contains(@title, 'Next')]/@href")
            if next_page:
                yield Request(next_page[0].extract(),\
                              callback=self.parse_listing_page)
        
        
    def parse_product_page(self, response):
        hxs = HtmlXPathSelector(response)  
        url = response.url    
        code = ''.join(hxs.select(".//*[@id='body-container']\
        /.//h1/span/text()").extract()).strip().strip('[]')
        
        name = ''.join(hxs.select(".//*[@id='body-container']\
        /.//h1/text()").extract()).strip()
        
        price = ''.join(hxs.select(".//*[@class='pricenowBIG']\
        /td/text()").extract()).strip()
        
        loader = ProductLoader(item=Product(), response=response)
        loader.add_value('sku', code)
        loader.add_value('name', name)
        loader.add_value('url', url)
        loader.add_value('price', price)
        yield loader.load_item()




