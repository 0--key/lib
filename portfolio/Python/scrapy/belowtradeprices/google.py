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
from scrapy import log

from pricecheck import valid_price

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

# google accounts 'btradeprices'[1..8] password: 'asdf1234..'

#KEYS = ('AIzaSyD5PHALB7OD7bR2Rvm0sb8HhtjkRrTILBE',
#        'AIzaSyDwHI0QVMop8dKXlYnORMN2KJJZOxKm1Y0',
#        'AIzaSyB25cc0Lzm3chfefaP_-nxR3GwrOpqncPQ',
#        'AIzaSyADBaY0g1XO8gPbn0dbboME6Pr_yHD45JM',
#        'AIzaSyABQhrpiwDmnl-i5YYOg_Ktad1qNFLpHu4',
#        'AIzaSyDMimMF4aATmGi51_OBRZs_hukC5Wn7xWI',
#        'AIzaSyD8zLuqj4pEAHacRJF5IownZ_cUxsZnglI',
#        'AIzaSyCeF6j5AK_TEbdyItcZVBOvEBu9kEYq6vw')

KEYS = ('AIzaSyDdvzwWzcxiw_EJ7Ud0yNwvlmdtfMmij38',
        'AIzaSyAt4anC-PBdP8HLKSosSoxQVPU29KAFrzo',
        'AIzaSyCihztLw4HaXy1QQ9NX9NZo1WWrSIAsxeg',
        'AIzaSyC9-zCcKeK7X1sCVlfX-H6YURsZoLzR_ms',
        'AIzaSyDKuhDZyU1fxPj1lJMPKYmmgzqkFYZiGcA',
        'AIzaSyARtkKxMBHISXLf10Msp9iDlPua7EdT8Wo',
        'AIzaSyDlx6V6n40BluLri2Iux0zm6t8y3_dbJbY',
        'AIzaSyAsUMf20iH1skLzk7upFYhupObdS7DzDNs')

FILTER_DOMAINS = ('belowtradeprices', 'ebid','cheaprshop','ilikegardens',
                  '247happyshopping','pricesava','shopprspot','toolstoday',
                  'bbcshop','dryburghcycles','ebay')

class GoogleSpider(BaseSpider):
    name = 'belowtradeprices-googleapis.com'
    allowed_domains = ['googleapis.com']

    def __init__(self, *args, **kwargs):
        super(GoogleSpider, self).__init__(*args, **kwargs)
        self.identifiers = {}
        with open(os.path.join(HERE, 'belowtrade.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.identifiers[row['url']] = row['sku']

    def start_requests(self):
        with open(os.path.join(HERE, 'product_skus.csv')) as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                sku = self.identifiers.get(row['url']) or row['sku']

                query = (row['search_q']).replace(' ', '+')
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
        
        #Extract the mpns of the first product.
        mpns = data['items'][0]['product'].get('mpns',[''])[0]
        if mpns:
            #Search for the lowest price for the products with the same mpns
            lowest = None
            data_mpns = {'items': [item for item in data['items'] if item['product'].get('mpns',[''])[0]==mpns]}
            while True:
                res = self._get_item(data_mpns, i, response)
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
        else:
            #Search for the first product with a valid price range.
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
                    if valid_price(response.meta['price'], pr['price']):
                        first_valid = pr
                        break
                    i += 1
            if first_valid:
                yield first_valid

    def _check_domain(self, domain, url):
        if domain in url:
            return True
