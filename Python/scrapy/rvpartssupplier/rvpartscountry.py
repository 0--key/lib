import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class RVPartsCountrySpider(BaseSpider):
    name = 'rvpartscountry.com'
    allowed_domains = ['www.rvpartscountry.com']
    start_urls = ('http://www.rvpartscountry.com/',)

    def __init__(self, *args, **kwargs):
        super(RVPartsCountrySpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://www.rvpartscountry.com/'

        # parse the csv file to get the product ids
        csv_file = csv.reader(open(os.path.join(HERE, 'monitored_products.csv')))

        product_re = re.compile('(.*)-(.*)')
        self.product_ids = [row[1] for row in csv_file]
        self.product_ids = self.product_ids[1:]
        self.product_ids = [''.join(product_re.match(id).groups()) for id in self.product_ids]

    def start_requests(self):
        for id in self.product_ids:
            url = self.URLBASE + 'search.asp?keyword=' + id + '&search=Go'
            request = Request(url)
            request.meta['sku'] = id
            yield request

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        url = hxs.select('//td[@align="center"]/a[not(contains(@href,"bigdaddy"))]/img/../@href').extract()
        if url:
            url = url[0]
            url = urljoin_rfc(self.URLBASE, url)
            request = Request(url, callback=self.parse_product)
            request.meta['sku'] = response.meta['sku']
            return request
        return


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        product_loader = ProductLoader(item=Product(), response=response)
        product_loader.add_value('name', response.meta['sku'])
        product_loader.add_xpath('price', '//div[@class="yourPrice"]/span[@class="salePriceContent"]/text()', re='.*\$(.*)')
        product_loader.add_xpath('price', '//div[@class="yourPrice"]/span[@class="itemPriceContent"]/text()', re='.*\$(.*)')
        product_loader.add_value('url', response.url)
        product_loader.add_value('sku', response.meta['sku'])
        return product_loader.load_item()