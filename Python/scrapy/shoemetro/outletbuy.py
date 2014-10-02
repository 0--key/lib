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
from scrapy import log

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class OutletBuySpider(BaseSpider):
    name = 'outletbuy.com'
    allowed_domains = ['outletbuy.com','www.outletbuy.com']

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
                query = row['name'].replace(' ', '+')
                url = 'http://www.outletbuy.com/s.jsp?Search=%s'
                yield Request(url % query, meta={'sku': sku, 'name': query})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        product = hxs.select('//table[@class="buybox"]')

        if not product:
            return

        loader = ProductLoader(item=Product(), selector=product)
        name = product.select('.//h1[@class="stylename"]/text()').extract()
        if name:
            log.msg(name[0].lower() + ' - ' + response.meta['name'].lower().replace('+', ' '))
            product_words = name[0].lower().strip().split(' ')
            search_words = response.meta['name'].lower().replace('+', ' ').split(' ')
            diff = [w for w in search_words if not w in product_words]
            #if name[0].lower() == response.meta['name'].lower().replace('+', ' '):
            if not diff:
                price = "".join(product.select('.//span[@class="price"]/span/text()').re(r'([0-9\,\. ]+)')).strip()
                loader.add_value('name', name[0])
                loader.add_value('url', response.url)
                loader.add_value('price', price)
                loader.add_value('sku', response.meta['sku'])

                if not 'apparelsave' in loader.get_output_value('name').lower():
                    yield loader.load_item()

