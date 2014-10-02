import re
import os
import csv
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log
from urlparse import urlparse
import time

HERE = os.path.abspath(os.path.dirname(__file__))

class TooledUpComSpider(BaseSpider):
    name = 'tooled-up.com-pro'
    allowed_domains = ['tooled-up.com', 'www.tooled-up.com']
    start_urls = ['http://www.tooled-up.com/']
    
    def parse(self, response):
        with open(os.path.join(HERE, 'tooled_up_com.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not len(row['url'].strip()):
                    continue
                
                log.msg('URL: %s' % row['url'])
                path = urlparse(row['url']).path
                log.msg('Path is %s' % path)
                if path == '/Product.asp':
                    request = Request(row['url'], callback=self.parse_product)
                    request.meta['sku'] = row['sku']
                    yield request
                elif path == '/SearchBasic.asp':
                    request = Request(row['url'], callback=self.parse_search)
                    request.meta['sku'] = row['sku']
                    yield request
                else:
                    log.msg('Unknown Path')
                    
    
    def parse_search(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)
        url = hxs.select('//div[@class="listingbox"]/p/a/@href').extract()[0]
        request = Request(urljoin_rfc(base_url, url), callback=self.parse_product)
        request.meta['sku'] = response.meta['sku']

        yield request
    
    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        
        product_loader = ProductLoader(item=Product(), response=response)
        product_loader.add_xpath('name', '//div[@class="headingbox"]/h1/text()')
        price = hxs.select('//span[@class="ourpricefeat"]/text()')
        if price:
            price_re = price.re('(\d+(?:\.\d+))')
            if price_re:
                product_loader.add_value('price', price_re[0])
        if not product_loader.get_output_value('price'):
            product_loader.add_value('price', 0)
        product_loader.add_value('sku', response.meta['sku'])
        product_loader.add_value('url', response.url)
        yield product_loader.load_item()
