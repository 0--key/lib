import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode

import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class WalmartSpider(BaseSpider):
    name = 'walmart.com'
    allowed_domains = ['www.walmart.com', 'walmart.com']
    #start_urls = ['http://www.walmart.com/browse/Grocery/976759?search_query=&ic=60_0&search_sort=1&cat_id=976759',
    #              'http://www.walmart.com/browse/Baby/5427?ic=60_0&tab_value=all&search_sort=1&cat_id=5427',
    #              'http://www.walmart.com/browse/Pharmacy/5431?ic=60_0&tab_value=all&search_sort=1&cat_id=5431']

    def start_requests(self):
        urls = ['http://www.walmart.com/browse/Grocery/976759?search_query=&ic=60_0&search_sort=1&cat_id=976759',
                'http://www.walmart.com/browse/Baby/5427?ic=60_0&tab_value=all&search_sort=1&cat_id=5427',
                'http://www.walmart.com/browse/Pharmacy/5431?ic=60_0&tab_value=all&search_sort=1&cat_id=5431']

        url = urls[0]
        urls = urls[1:]
        yield Request(url, meta={'cats': urls})

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        products = hxs.select(u'//div[@class="prodInfo"]')
        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//a[contains(@class,"prodLink")]/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)
            name = product.select(u'.//a[contains(@class,"prodLink")]/text()').extract()[0].strip()
            product_loader.add_value('name', name)
            try:
                price = product.select(u'.//div[@class="PriceContent"]//div[@class="camelPrice"]/span[@class="bigPriceText2"]/text()').re('\$(.*)')[0]
                price += product.select(u'.//div[@class="PriceContent"]//div[@class="camelPrice"]/span[@class="smallPriceText2"]/text()').extract()[0]
            except IndexError:
                price_big = product.select(u'.//div[@class="PriceContent"]//div[@class="camelPrice"]/span[@class="bigPriceTextOutStock2"]/text()').re('\$(.*)')
                price_small = product.select(u'.//div[@class="PriceContent"]//div[@class="camelPrice"]/span[@class="smallPriceTextOutStock2"]/text()').extract()
                if price_big and price_small:
                    price = price_big[0] + price_small[0]
                else:
                    continue
            product_loader.add_value('price', price)
            yield product_loader.load_item()
        
        # pages
        next_page = hxs.select(u'//a[@class="jump next"]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page, callback=self.parse, meta={'cats': response.meta['cats'][:]})
        elif response.meta.get('cats'):
            yield Request(response.meta['cats'][0], meta={'cats': response.meta['cats'][1:]})

