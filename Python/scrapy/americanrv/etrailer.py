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

class EtrailerSpider(BaseSpider):
    name = 'etrailer.com'
    allowed_domains = ['www.etrailer.com']
    start_urls = ('http://www.etrailer.com/',)

    def __init__(self, *args, **kwargs):
        super(EtrailerSpider, self).__init__(*args, **kwargs)
        csv_file = csv.reader(open(os.path.join(HERE, 'americanrv_products.csv')))
        csv_file.next()
        self.product_ids = {}
        for row in csv_file:
#           ids = row[3].split(' ')
#            if ids[0] == '':
#                ids = set()
#            else:
#                ids = set(ids)
            ids = set()
            ids.add(row[0])
            ids.add(row[2])
            self.product_ids[row[0]] = {'mfrgid': row[2], 'ids': frozenset(ids)}

    def start_requests(self):
        for sku, data in self.product_ids.items():
            for id in data['ids']:
                url = 'http://accessories.etrailer.com/search?w=' + re.sub(' ','+', id)
                req = Request(url, meta={'sku': sku, 'mfrgid': data['mfrgid']})
                yield req
            
    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # pagination
        # next_page = hxs.select(u'//a[@class="pageselectorlink" and contains(text(),"Next")]/@href').extract()
        # if next_page:
        #    next_page = urljoin_rfc(get_base_url(response), next_page[0])
        #    yield Request(next_page)

        # products
        for product in self.parse_product(response):
            yield product

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        products = hxs.select('//div[@class="summaryboxsearch"]')
        for product in products[0:1]: # extract only the first product
            product_loader = ProductLoader(item=Product(), selector=product)
            product_loader.add_xpath('price', u'.//span[@class="floatl sli_price"]/text()')
            product_loader.add_xpath('url', u'.//p[@class="mtext nobreak"]/a/@title')
            product_loader.add_value('sku', response.meta['sku'])
            product_loader.add_value('identifier', response.meta['sku'].lower())
            product_loader.add_xpath('name', u'.//p[@class="mtext nobreak"]/a/text()')
            name = product_loader.get_output_value('name').lower()
            sku = product_loader.get_output_value('sku').lower().split(' ')
            sku = filter(lambda x: x != '' and x in name, sku)
            site_mfrgid = product.select('.//span[@class="floatl sli_grid_code"]/text()').extract()
            if site_mfrgid:
                mfrgid = response.meta['mfrgid'].lower()
                site_mfrgid = site_mfrgid[0].strip().lower()
                if mfrgid in site_mfrgid and sku:
                    yield product_loader.load_item()

        if not products:
            product_loader = ProductLoader(item=Product(), response=response)
            product_loader.add_xpath('price', u'//p[@class="strong"]/span/text()')
            product_loader.add_value('url', response.url)
            product_loader.add_value('sku', response.meta['sku'])
            product_loader.add_value('identifier', response.meta['sku'].lower())
            product_loader.add_xpath('name', u'//div[@class="indentl orderbox"]//h1/text()')
            name = product_loader.get_output_value('name').lower()
            sku = product_loader.get_output_value('sku').lower().split(' ')
            sku = filter(lambda x: x != '' and x in name, sku)
            site_mfrgid = hxs.select('//div[@class="indentl orderbox"]/div[@class="floatl"]/p/strong/text()').extract()
            if site_mfrgid:
                site_mfrgid = site_mfrgid[0].strip().lower()
                mfrgid = response.meta['mfrgid'].lower()
                if mfrgid in site_mfrgid and sku:
                    yield product_loader.load_item()