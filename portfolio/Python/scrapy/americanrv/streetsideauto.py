import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class StreetSideAutoSpider(BaseSpider):
    name = 'streetsideauto.com'
    allowed_domains = ['www.streetsideauto.com']
    start_urls = ('http://www.streetsideauto.com/',)

    def __init__(self, *args, **kwargs):
        super(StreetSideAutoSpider, self).__init__(*args, **kwargs)

        csv_file = csv.reader(open(os.path.join(HERE, 'americanrv_products.csv')))
        csv_file.next()
        self.product_ids = {}
        for row in csv_file:
            ids = set()
            ids.add(row[0])
            self.product_ids[row[0]] = {'mfrgid': row[2], 'ids': frozenset(ids)}

    def start_requests(self):
        for sku, data in self.product_ids.items():
            for id in data['ids']:
                url = 'http://www.streetsideauto.com/search.asp?keywords=' + re.sub(' ','+', id)
                req = Request(url)
                req.meta['sku'] = sku
                req.meta['mfrgid'] = data['mfrgid']
                yield req
            
    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # pagination
        # next_page = hxs.select(u'//dl[@class="pages"]/dd/a[contains(text(),"Next")]/@href').extract()
        # if next_page:
            # next_page = urljoin_rfc(get_base_url(response), next_page[0])
            # req = Request(next_page, meta={'sku': response.meta['sku']})
            # yield req

        # products
        products = hxs.select(u'//div[@class="p-summary leaf"]/a[@class="part-title"]/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            req = Request(url, callback=self.parse_product)
            req.meta['sku'] = response.meta['sku']
            req.meta['mfrgid'] = response.meta['mfrgid']
            yield req



    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        product_loader = ProductLoader(item=Product(), response=response)

        product_loader.add_xpath('price', u'//div[@id="conv-box"]//dd[@class="amount"]/text()')
        if not product_loader.get_output_value('price'):
            product_loader.add_xpath('price', u'//dl[@class="ssa-price-dl"]/dd[@class="ssa-price"]/text()')
        product_loader.add_value('url', response.url)
        product_loader.add_value('sku', response.meta['sku'])
        product_loader.add_value('identifier', response.meta['sku'].lower())

        name = hxs.select(u'//div[@class="right-column-left"]/div[@class="title"]/h2/text()').extract()[0].strip()
        product_loader.add_value('name', name)

        # sku = response.meta['sku'].lower().split(' ')
        # name = product_loader.get_output_value('name').lower()
        # sku = filter(lambda x: x != '' and x in name, sku)
        part_number = hxs.select(u'//div[@class="title"]/h2/span/text()').re('Part No. (.*)')[0]
        mfrgid = response.meta['mfrgid']
        if part_number == mfrgid and product_loader.get_output_value('price'):
            yield product_loader.load_item()
