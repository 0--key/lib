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
    name = 'adventurerv.net'
    allowed_domains = ['www.adventurerv.net']
    start_urls = ('http://www.adventurerv.net/',)

    def __init__(self, *args, **kwargs):
        super(RVPartsCountrySpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://www.adventurerv.net/'

        # parse the csv file to get the product ids
        csv_file = csv.reader(open(os.path.join(HERE, 'monitored_products.csv')))

        self.product_ids = [row[3] for row in csv_file]
        self.product_ids = self.product_ids[1:]

    def start_requests(self):
        for id in self.product_ids:
            url = self.URLBASE + 'advanced_search_result.php?keywords=' + id
            yield Request(url)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        has_sku = True if hxs.select('//div[@id="content"]/div[@id="right-column"]/span[@class="right"]/text()') \
                       else False
        product_urls = hxs.select('//div[@class="product-listing-text"]/a/@href').extract()
        if product_urls:
            for url in product_urls:
                yield Request(url, callback=self.parse_product)
        elif has_sku:
                yield Request(response.url, callback=self.parse_product, dont_filter=True)
        else:
            return



    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        product_loader = ProductLoader(item=Product(), response=response)

        product_loader.add_xpath('price', '//div[@class="h3"]/span[@class="productSpecialPrice"]/text()',
                                 re='.*\$(.*)')
        product_loader.add_xpath('price', '//div[@class="h3"]/text()', re='.*\$(.*[0-9])')
        product_loader.add_value('url', response.url)
        product_loader.add_xpath('sku', '//div[@id="content"]/div[@id="right-column"]/span[@class="right"]/text()',
                                 re='-(.*)\]')

        sku = product_loader.get_output_value('sku')
        if sku:
            product_loader.add_value('name', sku)
        else:
            product_loader.add_xpath('name', '//div[@id="content"]/div[@id="right-column"]/h1[@class="bottom-border"]/text()')

        return product_loader.load_item()