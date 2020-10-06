#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Version 0.01
#       Started 09.08.2012
#       Autor   Roman <romis@wippies.fi>
from scrapy.http import Request
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoader

class Pondkeeper(BaseSpider):
    name = 'pondkeeper'
    allowed_domains = ['pondkeeper.co.uk']
    start_urls = ['http://www.pondkeeper.co.uk']


    def parse(self, response): 
        hxs = HtmlXPathSelector(response)
        urls = [x.strip() for x in hxs.select(".//*[@id='mainpageleft']/ul[1]/.//a/@href").extract() if x.strip()]+\
               [x.strip() for x in hxs.select(".//*[@id='mainpageleft']/ul[4]/.//a/@href").extract() if x.strip()]
        for url in urls:
            yield Request(url, callback=self.parse_category)
            
            
    def parse_category(self, response):
        hxs = HtmlXPathSelector(response)
        urls = [urljoin_rfc(get_base_url(response), x.strip()) for x in hxs.select(".//*[@id='pagecontentleft']/.//*[contains(@class, 'subcatlink')]/.//a[1]/@href").extract() if x.strip()]
        for url in urls:
            yield Request(url, callback=self.parse_subcategory)
        
        
    def parse_subcategory(self, response):
        hxs = HtmlXPathSelector(response)
        urls = [urljoin_rfc(get_base_url(response), x.strip()) for x in hxs.select(".//*[@class='prodnamelink']/a[1]/@href").extract() if x.strip()]
        if not urls:
            urls = [urljoin_rfc(get_base_url(response), x.strip()) for x in hxs.select(".//*[@id='pagecontentleft']/.//a[contains(text(), 'more info')]/@href").extract() if x.strip()]
        for url in urls:
            yield Request(url, callback=self.parse_product_page)         
       
        
    def parse_product_page(self, response):
        hxs = HtmlXPathSelector(response)  
        url = response.url
        
        out_of_stock = hxs.select(".//*[contains(text(), 'This product is currently out of stock')]/..")
        mul_price = hxs.select(".//table[@class='prodpagetable'][2]/.//*[@action='/addprod.asp' or @action='http://www.pondkeeper.co.uk/addprod.asp']/../..")
        price = ''.join(hxs.select(".//*[@id='prodprice']/.//text()").extract()[::-1]).split(u'\xa3')[-1].strip()
        
        if out_of_stock:
            base_name = ''.join(hxs.select(".//*[@id='pagecontentleft']/h1/text()").extract()).strip()
            price = ''.join(hxs.select(".//*[@id='prodprice']/.//text()").extract()[::-1]).split(u'\xa3')[-1].strip()
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('name', base_name)
            loader.add_value('url', url)
            loader.add_value('price', price)
            yield loader.load_item()    
        else:
            if price:
                base_name = ''.join(hxs.select(".//*[@id='pagecontentleft']/h1/text()").extract()).strip()
                loader = ProductLoader(item=Product(), response=response)
                loader.add_value('name', base_name)
                loader.add_value('url', url)
                loader.add_value('price', price)
                yield loader.load_item()  
                
        if mul_price:
            base_name = ''.join(hxs.select(".//*[@id='pagecontentleft']/h1/text()").extract()).strip()
            for el in mul_price:
                name = ''.join([base_name, ' ', '('] + [x.split(u'\xa3')[-1] for x in el.select(".//td/.//text()").extract() if x.strip() and u'\xa3' not in x]+[')']).strip()
                price = ''.join(hxs.select(".//*[@id='prodprice']/.//text()").extract()[::-1]).split(u'\xa3')[-1].strip()
                if not price:
                    price = ''.join([x.split(u'\xa3')[-1] for x in el.select(".//text()").extract() if  u'\xa3' in x])
                loader = ProductLoader(item=Product(), response=response)
                loader.add_value('name', name)
                loader.add_value('url', url)
                loader.add_value('price', price)
                yield loader.load_item() 
                
       
