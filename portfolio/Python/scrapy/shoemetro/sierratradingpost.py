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

class sierratradingpostSpider(BaseSpider):
    name = 'sierratradingpost.com'
    allowed_domains = ['sierratradingpost.com','www.sierratradingpost.com']

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
                url = 'http://www.sierratradingpost.com/product/search/%s'
                """
                query = row['name'].replace(' ', '-').lower()
                url = 'http://www.sierratradingpost.com/s~%s'
                yield Request(url % query, meta={'sku': sku, 'name': query})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)
        products = hxs.select('//div[@id="products"]/div/div[contains(@class,"productThumbnailContainer")]')

        if not products:
            return
        product = products[0]
        loader = ProductLoader(item=Product(), selector=product)
        name = product.select('.//div[@class="productTitle"]/a/text()').extract()
        if name:
            url = product.select('.//div[@class="productTitle"]/a/@href').extract()[0]
            price = "".join(product.select('.//span[@class="ourPrice"]/text()').re(r'([0-9\,\. ]+)')).strip()
            loader.add_value('name', name[0].strip())
            loader.add_value('url', urljoin_rfc(base_url,url))
            loader.add_value('price', price)
            loader.add_value('sku', response.meta['sku'])

            if not 'apparelsave' in loader.get_output_value('name').lower():
                yield loader.load_item()

