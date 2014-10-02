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

class AmazonCoUkSpider(BaseSpider):
    name = 'amazon.co.uk-bosch-pro'
    allowed_domains = ['amazon.co.uk', 'www.amazon.co.uk']
    start_urls = ['http://www.amazon.co.uk/']
    
    def parse(self, response):
        with open(os.path.join(HERE, 'amazon_co_uk.csv')) as f:
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
        product_loader.add_xpath('name', '//span[@id="btAsinTitle"]/text()')
        price = hxs.select('//span[@id="actualPriceValue"]//b/text()')
        if not price:
            price = hxs.select('//div[@id="secondaryUsedAndNew"]//span[@class="price"]//text()')
        if price:
            product_loader.add_value('price', price.extract()[0].replace(u'\xa3', ''))
        else:
            product_loader.add_value('price', 0)
        product_loader.add_value('sku', response.meta['sku'])
        product_loader.add_value('url', response.url)
        yield product_loader.load_item()
