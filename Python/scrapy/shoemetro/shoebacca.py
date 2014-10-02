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

class shoebaccaSpider(BaseSpider):
    name = 'shoebacca.com'
    allowed_domains = ['shoebacca.com','www.shoebacca.com']

    def start_requests(self):
        shutil.copy(os.path.join(HERE, 'shoemetroall.csv'),os.path.join(HERE, 'shoemetroall.csv.' + self.name + '.cur'))
        with open(os.path.join(HERE, 'shoemetroall.csv.' + self.name + '.cur')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['sku']
                """
                brand = row['brand']
                style = row['style']
                query = (brand + ' ' + style).replace(' ', '%20')
                """
                query = row['name'].replace(' ', '+')
                url = 'http://www.shoebacca.com/finder/?query=%s&search_form=1&sort=price-low-high'
                yield Request(url % query, meta={'sku': sku, 'name': query})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        products = hxs.select('//ul[@id="finder-data"]/li')

        if not products:
            return
        product = products[0]

        loader = ProductLoader(item=Product(), selector=product)
        name = "".join(product.select('./a/div/h5/span/text()').extract())
        if name:
            name2 = "".join(product.select('./a/div/h5/text()').extract())
            url = product.select('./a/@href').extract()[0]
            price = "".join(product.select('./a/div[@class="p-price"]/text()').re(r'([0-9\,\. ]+)')).strip()
            if not price:
                price = "".join(product.select('./a/div[@class="p-price"]/span[@class="sale-price"]/text()').re(r'([0-9\,\. ]+)')).strip()
            loader.add_value('name', name.strip() + ' ' + name2.strip())
            loader.add_value('url', urljoin_rfc(base_url,url))
            loader.add_value('price', price)
            loader.add_value('sku', response.meta['sku'])

            if not 'apparelsave' in loader.get_output_value('name').lower():
                yield loader.load_item()

