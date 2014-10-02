import csv
import os
import copy

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy import log


from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

CATS = {'Books': 'stripbooks', 'eBooks': 'digital-text',
        'DVD/Video': 'dvd', 'eMagazines': 'digital-text',
        'Games': 'software', 'Music': 'popular',
        'Software': 'software', 'Toys': 'toys'}

class AmazonSpider(BaseSpider):
    name = 'kalahari-amazon.co.uk'
    allowed_domains = ['amazon.co.uk']

    def start_requests(self):
        with open(os.path.join(HERE, 'products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['ProdCode']

                cat = CATS.get(row['ProductType'], 'aps')
                query = row['Title'].replace(' ', '+')
                query = sku
                url = 'http://www.amazon.co.uk/s/ref=nb_sb_noss?' + \
                      'url=search-alias%%3D%s&field-keywords=%s&x=0&y=0'

                yield Request(url % (cat, query), meta={'sku': sku})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//div[@id="atfResults"]//div[starts-with(@id, "result_")]')
        pr = None
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', './/h3[@class="title"]/a/text()')

            loader.add_xpath('url', './/h3[@class="title"]/a/@href')
            loader.add_xpath('price', './/td[@class="toeOurPrice"]/a/text()')
            loader.add_value('sku', response.meta['sku'])

            if loader.get_output_value('price') and (pr is None or pr.get_output_value('price') >
                                                                   loader.get_output_value('price')):
                pr = loader

        if pr:
            yield pr.load_item()

