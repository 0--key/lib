import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc


import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class CampingWorldSpider(BaseSpider):
    name = 'campingworld-americanrv.com'
    allowed_domains = ['www.campingworld.com']
    start_urls = ('http://www.campingworld.com/',)

    def __init__(self, *args, **kwargs):
        super(CampingWorldSpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://www.campingworld.com/'

        # parse the csv file to get the product ids
        csv_file = csv.reader(open(os.path.join(HERE, 'americanrv_products.csv')))
        csv_file.next()
        self.product_ids = {}
        for row in csv_file:
            ids = row[3].split(' ')
            if ids[0] == '':
                ids = set()
            else:
                ids = set(ids)
            ids.add(row[0])
            ids.add(row[2])
            self.product_ids[row[0]] = {'mfrgid': row[2], 'name': row[1], 'ids': frozenset(ids)}

    def start_requests(self):
        for sku, data in self.product_ids.items():
            for id in data['ids']:
                url = self.URLBASE + 'search/index.cfm?Ntt=' + id + '&N=0&Ntx=mode+matchallpartial&Ntk=primary&Nty=1&Ntpc=1'
                req = Request(url, callback=self.parse_product)
                req.meta['sku'] = sku
                req.meta['mfrgid'] = data['mfrgid']
                req.meta['name'] = data['name']
                yield req

    def parse(self, response):
        return



    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        product_loader = ProductLoader(item=Product(), response=response)
        product_loader.add_xpath('name', '//h1[@itemprop="name"]/text()')
        product_loader.add_xpath('price', '//div[@class="club"]/span[@itemprop="Price"]/text()',
                                 re='.*\$(.*[0-9])')
        product_loader.add_value('url', response.url)
        product_loader.add_value('sku', response.meta['sku'])
        product_loader.add_value('identifier', response.meta['sku'].lower())
        if not product_loader.get_output_value('price'):
            return
        mfrgid = response.meta['mfrgid']
        if product_loader.get_output_value('name'):
            site_mfrgid = hxs.select(u'//p[@class="specs" and child::span[contains(text(),"Mfg Part")]]/text()').extract()
            site_mfrgid = site_mfrgid[1] if len(site_mfrgid) >= 2 else None
            name = response.meta['name'].split(' ')
            if site_mfrgid and (mfrgid == site_mfrgid.strip() or site_mfrgid in name):
                return product_loader.load_item()