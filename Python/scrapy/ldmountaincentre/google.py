import csv
import os
import copy
import json
from decimal import Decimal

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http.cookies import CookieJar
from pricecheck import valid_price

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))


KEYS = ('AIzaSyByntiQdJrTyFw78jaVS6-IdMqMuISqX5Y',
        'AIzaSyBK8RtRt-v1JHYhbPszQDv2LlAbIZHuyMo',
        'AIzaSyDbmM13l-e_f7bpJH3D6bynBhedKfwszYo')

FILTER_DOMAINS = ('ldmountaincentre', 'ebay')

class GoogleSpider(BaseSpider):
    name = 'ldmountaincentre-googleapis.com'
    allowed_domains = ['googleapis.com']

    def start_requests(self):
        with open(os.path.join(HERE, 'product_skus.csv')) as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                sku = row['sku']

                query = (row['name']).replace(' ', '+')
                url = 'https://www.googleapis.com/shopping/search/v1/public/products' + \
                      '?key=%s&country=GB&' + \
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
        lowest = None
        while True:
            res = self._get_item(data, i, response)
            if not res:
                break
            pr = res[0]
            item = res[1]
            invalid_domain = any([self._check_domain(domain, pr['url']) for domain in FILTER_DOMAINS])
            if invalid_domain:
                i += 1
            else:
                if valid_price(response.meta['price'], pr['price']) and \
                    (lowest is None or lowest['price'] > pr['price']):
                    lowest = pr
                i += 1
        if lowest:
            yield lowest

    def _check_domain(self, domain, url):
        if domain in url:
            return True
