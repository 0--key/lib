#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Version 0.01
#       Started 09.08.2012
#       Autor   Roman <romis@wippies.fi>
import re
from scrapy.http import Request
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoader

class SwallowaquaticsSpider(BaseSpider):
    name = 'swallowaquatics'
    allowed_domains = ['swallowaquatics.co.uk']
    start_urls = ['http://www.swallowaquatics.co.uk/site-map.aspx']

    def parse(self, response): 
        hxs = HtmlXPathSelector(response)
        urls = [urljoin_rfc(get_base_url(response), x.strip()) for x in hxs.select(".//*[@id='clSiteMap_lblSiteMap']/div/a/@href").extract() if x.strip()]
        for url in set(urls):
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_listing_page)


    def parse_listing_page(self, response):
        hxs = HtmlXPathSelector(response)
        product_urls = [x for x in hxs.select(".//*[@class='product']/div[1]/a/@href").extract() if x]
        if product_urls:
            for product_url in product_urls:
                product_url = urljoin_rfc(get_base_url(response), product_url)
                yield Request(product_url, callback=self.parse_product_page)
                
            next_page = hxs.select(".//div[@id='rightnav']/a[contains(text(), 'More Products')]/@href")
            if next_page:
                next_url = urljoin_rfc(get_base_url(response), next_page[0].extract())
                yield Request(next_url, callback=self.parse_listing_page)
        
        
    def parse_product_page(self, response):
        hxs = HtmlXPathSelector(response)  
        url = response.url   
        name = ''.join(hxs.select(".//*[@id='ProductDetail21_trProductName']/td/h1/text()").extract()).strip()
        price = ''.join(hxs.select(".//*[@id='ProductDetail21_pricing1_lblSalePrice']/text()").extract()).strip()
        options = hxs.select(".//*[@id='ProductDetail21_CAttributeControl1_DlAttributes_ctl00_AttributeName']/option")
        if options:
            for option in options[1:]:
                option_text = option.select(".//text()").extract()[0]
                option_price = ''.join(re.findall(u'\xa3(.*)\)', option_text))
                option_name = ' '.join([name, option_text.split(option_price)[0].rstrip(u'( \xa3')])
                loader = ProductLoader(item=Product(), response=response)
                loader.add_value('name', option_name)
                loader.add_value('url', url)
                loader.add_value('price', option_price)
                yield loader.load_item()
        else:
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('name', name)
            loader.add_value('url', url)
            loader.add_value('price', price)
            yield loader.load_item()

