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
    name = 'campingworld.com'
    allowed_domains = ['www.campingworld.com']
    start_urls = ('http://www.campingworld.com/',)

    def __init__(self, *args, **kwargs):
        super(CampingWorldSpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://www.campingworld.com/'

        # parse the csv file to get the product ids
        csv_file = csv.reader(open(os.path.join(HERE, 'monitored_products.csv')))

        self.product_ids = [row[3] for row in csv_file]
        self.product_ids = self.product_ids[1:]

    def start_requests(self):
        for id in self.product_ids:
            url = self.URLBASE + 'search/index.cfm?Ntt=' + id + '&N=0&Ntx=mode+matchallpartial&Ntk=primary&Nty=1&Ntpc=1'
            yield Request(url, callback=self.parse_product)

    def parse(self, response):
        return



    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        product_loader = ProductLoader(item=Product(), response=response)
        product_loader.add_xpath('name', '//h1[@itemprop="name"]/text()')
        product_loader.add_xpath('price', '//div[@class="club"]/span[@itemprop="Price"]/text()',
                                 re='.*\$(.*[0-9])')
        product_loader.add_value('url', response.url)
        return product_loader.load_item()