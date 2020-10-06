import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class AdventureRVAMRVSpider(BaseSpider):
    name = 'adventurerv-americanrv.net'
    allowed_domains = ['www.adventurerv.net']
    start_urls = ('http://www.adventurerv.net/',)

    def __init__(self, *args, **kwargs):
        super(AdventureRVAMRVSpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://www.adventurerv.net/'

        # parse the csv file to get the product ids
        csv_file = csv.reader(open(os.path.join(HERE, 'americanrv_products.csv')))
        csv_file.next()
        self.product_ids = {}
        for row in csv_file:
            ids = set()
            ids.add(row[0])
            ids.add(row[2])
            self.product_ids[row[0]] = {'mfrgid': row[2], 'name': row[1], 'ids': frozenset(ids)}



    def start_requests(self):
        for sku, data in self.product_ids.items():
            for id in data['ids']:
                url = self.URLBASE + 'advanced_search_result.php?keywords=' + id
                req = Request(url, dont_filter=True)
                req.meta['sku'] = sku
                req.meta['mfrgid'] = data['mfrgid']
                req.meta['name'] = data['name']
                yield req

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        has_sku = True if hxs.select(u'//div[@id="content"]/div[@id="right-column"]/span[@class="right"]/text()') \
                       else False
        product_urls = hxs.select(u'//div[@class="product-listing-text"]/a/@href').extract()
        if product_urls:
            for url in product_urls:
                req = Request(url, callback=self.parse_product, dont_filter=True)
                req.meta['sku'] = response.meta['sku']
                req.meta['mfrgid'] = response.meta['mfrgid']
                req.meta['name'] = response.meta['name']
                yield req
        elif has_sku:
            req = Request(response.url, callback=self.parse_product, dont_filter=True)
            req.meta['sku'] = response.meta['sku']
            req.meta['mfrgid'] = response.meta['mfrgid']
            req.meta['name'] = response.meta['name']
            yield req
        else:
            return



    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        product_loader = ProductLoader(item=Product(), response=response)

        product_loader.add_xpath('price', u'//div[@class="h3"]/span[@class="productSpecialPrice"]/text()',
                                 re='.*\$(.*)')
        product_loader.add_xpath('price', u'//div[@class="h3"]/text()', re='.*\$(.*[0-9])')
        product_loader.add_value('url', response.url)
        product_loader.add_value('sku', response.meta['sku'])
        product_loader.add_value('identifier', response.meta['sku'].lower())

        product_loader.add_xpath('name', u'//div[@id="right-column"]/h1/text()')
        site_mfrgids = hxs.select('//div[@id="right-column"]/div[@class="right" and contains(text(),"Manufacturer\'s Number")]/text()').re('Number: (.*)')
        if site_mfrgids:
            site_mfrgids = site_mfrgids[0].lower()
        else:
            return
        site_mfrgids = site_mfrgids.split(' ')
        # name = response.meta['name'].split(' ')
        # name_condition = False
        # for site_mfrgid in site_mfrgids:
        #     if site_mfrgid in name:
        #         name_condition = True
        #         break
        if response.meta['mfrgid'].lower().strip() in site_mfrgids: # or name_condition:
            yield product_loader.load_item()