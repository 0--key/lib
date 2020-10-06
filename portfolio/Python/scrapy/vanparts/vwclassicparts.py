import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class VWClassicPartsSpider(BaseSpider):
    name = 'vw-classicparts.de'
    allowed_domains = ['http://www.vw-classicparts.de', 'www.vw-classicparts.de']
    start_urls = ('http://www.vw-classicparts.de/',)

    def __init__(self, *args, **kwargs):
        super(VWClassicPartsSpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://www.vw-classicparts.de/'

        # parse the csv file to get the product ids
        csv_file = csv.reader(open(os.path.join(HERE, 'monitored_products.csv')))

        self.product_ids = [row[0] for row in csv_file]
        self.product_ids = self.product_ids[1:]
        self.product_ids = [re.sub('[\- \.]', '', product_id) for product_id in self.product_ids]

    def start_requests(self):
        url = 'http://www.vw-classicparts.de/bestand/bestand_int.pl?lang=en'
        yield Request(url, callback=self.search_requests)

    def search_requests(self, response):
        for product_id in self.product_ids:
            form_name = 'formular'
            form_data = {'teilenummer': product_id}
            form_request = FormRequest.from_response(response, formname=form_name, formdata=form_data, dont_click=True,
                                                     dont_filter=True, priority=1)
            form_request.meta['sku'] = product_id
            yield form_request

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        
        products = hxs.select('//table/tr/td[@bgcolor="#dddddd"]/..')
        for product in products:
            try:
                product = product.select('./td')
                product_loader = ProductLoader(item=Product(), selector=product)
                name = product[1].select('./small/text()').extract()[0].strip()
                if response.meta['sku']:
                    product_loader.add_value('name', response.meta['sku'].lower())
                else:
                    product_loader.add_value('name', name)
                price = product[3].select('./small/text()').re('(.*[0-9])')
                product_loader.add_value('price', price)
                product_loader.add_value('sku', response.meta['sku'])
                product_loader.add_value('url', '')
                yield product_loader.load_item()
            except IndexError:
               continue
            return