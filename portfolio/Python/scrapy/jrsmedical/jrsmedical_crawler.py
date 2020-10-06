import csv
import os
import copy
import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http.cookies import CookieJar

from scrapy import log

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class JRSMedicalSpider(BaseSpider):
    name = 'jrsmedical.com'
    allowed_domains = ['jrsmedical.com']

    def start_requests(self):
        with open(os.path.join(HERE, 'jrsmedical_products.csv')) as f:
            reader = csv.reader(f)
            reader.next()
            for row in reader:
                url = row[0]
                sku = row[1]
                if url:
                    yield Request(url, meta={'sku': sku}, callback=self.parse_product, dont_filter=True)

    def parse(self, response):
        pass

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        product_options = hxs.select(u'//td[@class="price"]/../..')
        for product_option in product_options:
            loader = ProductLoader(item=Product(), selector=product_option)
            sku = response.meta['sku']
            site_sku = hxs.select(u'.//td[@class="LineTitle"]/span/text()').extract()[0].strip()
            name = product_option.select(u'//td[@class="ProductTitle"]/span/text()').extract()[0].strip()
            option_name = product_option.select(u'.//tr[contains(@id,"LineInfo")]//span/text()').extract()

            if not option_name:
                log.msg('Option name not present [%s]' % response.url)

            option_name = ' '.join(option_name)
            name += ' ' + option_name.strip() + ' (%s)' % sku
            loader.add_value('name', name)
            loader.add_xpath('price', u'.//td[@class="price"]/span/text()')
            loader.add_value('url', response.url)
            loader.add_value('sku', sku)
            if sku == site_sku:
                yield loader.load_item()
