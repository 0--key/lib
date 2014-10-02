import re
import os
from decimal import Decimal

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from urllib import urlencode
import hashlib
import shutil

import csv

from product_spiders.items import Product, ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class AmericanRVSpider(BaseSpider):
    name = 'americanrvcompany_americanrv.com'
    allowed_domains = ['www.americanrvcompany.com', 'americanrvcompany.com']
    start_urls = ('http://www.americanrvcompany.com/search.asp?keyword=%25%25&search.x=45&search.y=39',)

    def __init__(self, *args, **kwargs):
        super(AmericanRVSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        csv_file = csv.reader(open(os.path.join(HERE, 'americanrv_products.csv')))
        self.skus_dict = {}
        csv_file.next()
        for row in csv_file:
            md5 = hashlib.md5()
            md5.update(row[1].strip())
            hashed_name = md5.hexdigest()
            sku = row[0]
            self.skus_dict[hashed_name] = sku

    def spider_closed(self, spider):
        if spider.name == self.name:
            shutil.copy('data/%s_products.csv' % spider.crawl_id, os.path.join(os.path.dirname(HERE),
                        'dyersonline/americanrv.csv'))
            log.msg("CSV is copied")

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # pagination
        next_page = hxs.select(u'//a[contains(text(),"Next Page")]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0].replace('%%', '%25%25'))
            yield Request(next_page)

        # products
        products = hxs.select(u'//td[@width="120"]/a/@href').extract()
        for product in products:
            product = urljoin_rfc(get_base_url(response), product)
            yield Request(product, callback=self.parse_product)
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        product_loader = ProductLoader(item=Product(), response=response)
        product_loader.add_value('url', response.url)
        product_loader.add_xpath('name', u'//td[@class="page_headers"]/text()')
        product_loader.add_xpath('price', u'//td[@class="price-info"]//div[@id="price" and @class="price"]/text()',
                                 re=u'\$(.*)')
        name = product_loader.get_output_value('name').strip()
        md5 = hashlib.md5()
        md5.update(name)
        hashed_name = md5.hexdigest()
        sku = self.skus_dict[hashed_name]
        product_loader.add_value('sku', sku)
        product_loader.add_xpath('sku', u'//span[@id="product_id"]/text()')
        product_loader.add_value('identifier', product_loader.get_output_value('sku').lower())
        loaded = (product_loader.get_output_value('name')) and (product_loader.get_output_value('price'))
        if loaded:
            yield product_loader.load_item()
        else:
            return