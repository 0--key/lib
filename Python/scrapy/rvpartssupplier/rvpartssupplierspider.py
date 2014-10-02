import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))


class RVPartsSupplierSpider(BaseSpider):
    name = 'rvpartssupplier.com'
    allowed_domains = ['www.rvpartssupplier.com']
    start_urls = ('http://www.rvpartssupplier.com/',)

    def __init__(self, *args, **kwargs):
        super(RVPartsSupplierSpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://www.rvpartssupplier.com/'

        # parse the csv file to get the product ids
        csv_file = csv.reader(open(os.path.join(HERE, 'monitored_products.csv')))

        product_re = re.compile('(.*)-(.*)')
        self.product_ids = [row[1] for row in csv_file]
        self.product_ids = self.product_ids[1:]
        self.product_ids = [''.join(product_re.match(id).groups()) for id in self.product_ids]

    def start_requests(self):
        for id in self.product_ids:
            url = self.URLBASE + 'product-p/' + id + '.html'
            yield Request(url, callback=self.parse_product)

    def parse(self, response):
        return

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        product_loader = ProductLoader(item=Product(), response=response)

        product_loader.add_xpath('price', '//font[@class="pricecolor colors_productprice"]/text()', re='.*\$(.*[0-9])')
        product_loader.add_value('url', response.url)
        product_loader.add_xpath('sku', '//span[@class="product_code"]/text()')

        sku = product_loader.get_output_value('sku')
        if sku:
            product_loader.add_value('name', sku)
        else:
            product_loader.add_xpath('name', '//font[@class="productnamecolorLARGE colors_productname"]/text()')

        return product_loader.load_item()