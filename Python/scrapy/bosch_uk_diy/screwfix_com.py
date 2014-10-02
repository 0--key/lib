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

class ScrewfixComSpider(BaseSpider):
    name = 'screwfix.com-diy'
    allowed_domains = ['screwfix.com', 'www.screwfix.com']
    start_urls = ['http://www.screwfix.com/']
    
    def parse(self, response):
        with open(os.path.join(HERE, 'screwfix_com.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not len(row['url'].strip()):
                    continue
                
                url = re.sub(r'#.+$', '', row['url'])
                log.msg('URL: %s' % url)
                request = Request(url, callback=self.parse_product)
                request.meta['sku'] = row['sku']
                yield request
    
    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        
        product_loader = ProductLoader(item=Product(), selector=hxs)
        product_loader.add_xpath('name', '//h1[@id="product_description"]/text()')
        product_loader.add_value('price', hxs.select('//p[@id="product_price"]/span/text()').re('(\d+(?:\.\d+))')[0])
        product_loader.add_value('sku', response.meta['sku'])
        product_loader.add_value('url', response.url)
        yield product_loader.load_item()