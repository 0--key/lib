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

class ToolStopCoUkSpider(BaseSpider):
    name = 'toolstop.co.uk-diy'
    allowed_domains = ['toolstop.co.uk', 'www.toolstop.co.uk']
    start_urls = ['http://www.toolstop.co.uk/?gl=gb']
    
    def parse(self, response):
        with open(os.path.join(HERE, 'toolstop_co_uk.csv')) as f:
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
        
        product_list = hxs.select('//div[@id="product_list"]/div[contains(@class,"product_item")]//div[@class="liked_product_name"]//a/@href').extract()
        if product_list:
            request = Request(urljoin_rfc(base_url, product_list[0]), callback=self.parse_product)
            request.meta['sku'] = response.meta['sku']
            yield request
        else:
            product_loader = ProductLoader(item=Product(), response=response)
            product_loader.add_xpath('name', '//h1[@id="product_name"]/text()')
            product_loader.add_value('price',hxs.select('//ul[@class="product_price"]/li[@class="inc_tax_red"]').re('(\d+(?:\.\d+))')[0])
            product_loader.add_value('sku', response.meta['sku'])
            product_loader.add_value('url', response.url)
            yield product_loader.load_item()
