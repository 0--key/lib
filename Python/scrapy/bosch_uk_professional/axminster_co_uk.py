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

class AxminsterSpider(BaseSpider):
    name = 'axminster.co.uk-pro'
    allowed_domains = ['axminster.co.uk', 'www.axminster.co.uk']
    start_urls = ['http://www.axminster.co.uk/']
    
    def parse(self, response):
        with open(os.path.join(HERE, 'axminster_co_uk.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not len(row['url'].strip()):
                    continue
                url = re.sub(r'#.+$', '', row['url'])
                log.msg('URL: %s' % url)
                if urlparse(url).scheme != 'http':
                    continue
                request = Request(url, callback=self.parse_product)
                request.meta['sku'] = row['sku']
                yield request

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)
        
        product_loader = ProductLoader(item=Product(), response=response)
        product_loader.add_xpath('name', '//div[@id="prodTITLE"]//h1/text()')
        product_loader.add_xpath('price', '//div[@id="prodDETAILS"]//span[@class="price"]/text()')
        product_loader.add_value('sku', response.meta['sku'])
        product_loader.add_value('url', response.url)
        yield product_loader.load_item()
