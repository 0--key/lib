import csv
import os
import copy
import json
import shutil
from decimal import Decimal

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http.cookies import CookieJar
from ignore_words import accept_product
from pricecheck import valid_price

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

KEYS = ['AIzaSyDO5Aexx0MSy-HK9DR0qPtPeAcAoYsySVw', 'AIzaSyC3nAW89B5XploEG7VNrh1ULHRzDej48jc',
        'AIzaSyCUXjfTHuYpcdWqSgjEdbbqc0aoGwB9BU4', 'AIzaSyCrtXscq-63qUo2_EzeWwHSc3WqwV9vOfw',
        'AIzaSyALAmLv-TqK9oVDW3PeYBDImq99kDz4tLU', 'AIzaSyBRZ-tQuwQF84PLq8DN4U9n8qLIus5f_64',
        'AIzaSyB-zCvXGR7cOgltdcRyllsr8y5-DgY4SgE']

class GoogleSpider(BaseSpider):
    name = 'shoemetro-googleapis.com'
    allowed_domains = ['googleapis.com']

    def start_requests(self):
        shutil.copy(os.path.join(HERE, 'shoemetroall.csv'),os.path.join(HERE, 'shoemetroall.csv.' + self.name + '.cur'))
        with open(os.path.join(HERE, 'shoemetroall.csv.' + self.name + '.cur')) as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                sku = row['sku']
                """
                query = (row['brand style']).replace(' ', '+')
                """
                query = row['name'].replace(' ', '+')
                url = 'https://www.googleapis.com/shopping/search/v1/public/products' + \
                      '?key=%s&country=US&' + \
                      'q=%s&restrictBy=condition=new'

                yield Request(url % (KEYS[i % len(KEYS)], query), meta={'sku': sku,
                                                                        'price': row['price'].replace('$', '')})

    def _get_item(self, data, i, response):
        if i >= len(data.get('items', [])):
            return

        item = data['items'][i]
        pr = Product()
        pr['name'] = (item['product']['title'] + ' ' + item.get('product', {}).get('author', {}).get('name', '')).strip()
        pr['url'] = item['product']['link']


        pr['price'] = Decimal(str(data['items'][i]['product']['inventories'][0]['price']))
        pr['sku'] = response.meta['sku']
        pr['identifier'] = response.meta['sku']

        return pr, item

    def parse(self, response):
        data = json.loads(response.body)

        i = 0
        while True:
            res = self._get_item(data, i, response)
            if not res:
                return

            pr = res[0]
            item = res[1]
            if 'apparelsave' in item['product']['author']['name'].lower() or \
               'shoemetro.com' in pr['url']:
                i += 1
            else:
                if valid_price(response.meta['price'], pr['price']):
                    yield pr
                    return
                else:
                    i += 1



