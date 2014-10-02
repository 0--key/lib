import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class AnyRVPartsSpider(BaseSpider):
    name = 'anyrvparts.com'
    allowed_domains = ['www.anyrvparts.com']
    start_urls = ('http://www.anyrvparts.com/',)

    def __init__(self, *args, **kwargs):
        super(AnyRVPartsSpider, self).__init__(*args, **kwargs)

        csv_file = csv.reader(open(os.path.join(HERE, 'americanrv_products.csv')))
        csv_file.next()
        self.product_ids = {}
        for row in csv_file:
            ids = set()
            ids.add(row[0])
            ids.add(row[2])
            self.product_ids[row[0]] = {'mfrgid': row[2], 'name': row[1], 'ids':frozenset(ids)}

    def start_requests(self):
        for sku, data in self.product_ids.items():
            for id in data['ids']:
                url = 'http://www.anyrvparts.com/FindaProduct.asp?ProductDescription=' + re.sub(' ','+', id)
                req = Request(url)
                req.meta['sku'] = sku
                req.meta['mfrgid'] = data['mfrgid']
                req.meta['name'] = data['name']
                yield req
            
    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # pagination
        # next_page = hxs.select(u'//a[child::font[contains(text(),"Next")]]/@href').extract()
        # if next_page:
            # next_page = urljoin_rfc(get_base_url(response), next_page[0])
            # yield Request(next_page)

        # products
        products = hxs.select(u'//a[contains(@href,"ProductDetail") and child::b]/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            req = Request(url, callback=self.parse_product)
            req.meta['sku'] = response.meta['sku']
            req.meta['mfrgid'] = response.meta['mfrgid']
            req.meta['name'] = response.meta['name']
            yield req



    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        product_loader = ProductLoader(item=Product(), response=response)

        product_loader.add_xpath('price', u'//td[@align="center"]//b[contains(text(),"$")]/text()',
                                 re=u'\$(.*)')
        product_loader.add_value('url', response.url)
        product_loader.add_value('sku', response.meta['sku'])
        product_loader.add_value('identifier', response.meta['sku'].lower())

        product_loader.add_xpath('name', u'//h1/text()')
        site_mfrgid = hxs.select(u'//nobr/b/text()').extract()
        mfrgid = response.meta['mfrgid']
        name = response.meta['name'].split(' ')
        if site_mfrgid and (site_mfrgid[0] == mfrgid or site_mfrgid[0] in name):
            return product_loader.load_item()