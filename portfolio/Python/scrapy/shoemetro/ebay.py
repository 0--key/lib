import csv
import os
import copy
import shutil

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http.cookies import CookieJar

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log

from pricecheck import valid_price

HERE = os.path.abspath(os.path.dirname(__file__))

class EbaySpider(BaseSpider):
    name = 'shoemetro-ebay.com'
    allowed_domains = ['ebay.com']
    user_agent = 'spd'
    #download_delay = 0.5

    def start_requests(self):
        shutil.copy(os.path.join(HERE, 'shoemetroall.csv'),os.path.join(HERE, 'shoemetroall.csv.' + self.name + '.cur'))
        with open(os.path.join(HERE, 'shoemetroall.csv.' + self.name + '.cur')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['sku']
                """
                brand = row['brand']
                style = row['style']
                query = (brand + ' ' + style).replace(' ', '+')
                """
                query = row['name'].replace(' ','+')
                #url = 'http://www.ebay.com/sch/Clothing-Shoes-Accessories-/11450/i.html?'+\
                #      '_sadis=200&_ipg=50&_skipfnorm=1&LH_SALE_CURRENCY=0&_clu=2&_ftrt=901'+\
                #      '&_ftrv=1&_adv=1%%7C1&gbr=1&_nkw=%(q)s&_dmd=1&LH_PrefLoc=2&_sop=12'
                url = 'http://www.ebay.com/sch/i.html?'+\
                      '_odkw=%(q)s&_sadis=200&_ipg=50&_skipfnorm=1&LH_SALE_CURRENCY=0'+\
                      '&_clu=2&_ftrt=901&_ftrv=1&_adv=1%%7C1&_sop=15&gbr=1&_osacat=0&LH_PrefLoc=2'+\
                      '&_dmd=1&_trksid=p2045573.m570.l1313&_nkw=%(q)s&_sacat=11450'


                yield Request(url % {'q': query}, meta={'sku': sku, 'price': row['price'].replace('$', '')})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        product = hxs.select('//td[@r="1"]')
        if not product:
            product = hxs.select('//table[@r="1"]')

        if not product and response.meta.get('_retries', 0) >= 3:
            #log.msg('ALERT! ' + response.url)
            #f = open(os.path.join(HERE, response.meta['sku'] + '.html'), 'w')
            #f.write(response.body)
            #f.close()

            return
        elif not product:
            retries = response.meta.get('_retries', 0)
            yield Request(response.url, meta={'sku': response.meta['sku'],
                                              '_retries': retries + 1},
                                              dont_filter=True)
            return

        loader = ProductLoader(item=Product(), selector=product)
        loader.add_xpath('name', './/div[@class="ittl"]//a[@class="vip"]/text()')
        loader.add_xpath('url', './/div[@class="ittl"]//a[@class="vip"]/@href')
        loader.add_xpath('price', './/div[@class="prices"]//span[@class="amt"]/text()')
        loader.add_xpath('price', './/div[@class="prices"]//span[@class="g-b amt"]/text()')
        loader.add_xpath('price', './/td[@class="prc"]//div[@class="g-b"]/text()')
        loader.add_xpath('price', './/*[@itemprop="price"]/text()')
        loader.add_value('sku', response.meta['sku'])
        loader.add_value('identifier', response.meta['sku'])

        if not 'apparelsave' in loader.get_output_value('name').lower() \
           and valid_price(response.meta['price'], loader.get_output_value('price')):
            yield loader.load_item()

