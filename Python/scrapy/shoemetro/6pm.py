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

class sixpmSpider(BaseSpider):
    name = '6pm.com'
    allowed_domains = ['6pm.com','www.6pm.com']

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
                url = 'http://www.6pm.com/search?term=%s'
                #'proxy': 'http://23.19.153.177:3128'
                yield Request(url % query, meta={'sku': sku, 'name': query})

    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        product = hxs.select('//div[@class="product-page"]')
        if product:
            loader = ProductLoader(item=Product(), selector=product)
            name = product.select('.//h1[@class="main-heading standard-header"]/a/text()').extract()
            name2 = product.select('.//h1[@class="main-heading standard-header"]/text()').extract()
            if name:
                price = "".join(product.select('.//span[@id="price"]/text()').re(r'([0-9\,\. ]+)')).strip()
                loader.add_value('name', name[0].strip() + ' ' + name2[0].strip())
                loader.add_value('url', response.url)
                loader.add_value('price', price)
                loader.add_value('sku', response.meta['sku'])
                if not 'apparelsave' in loader.get_output_value('name').lower():
                    yield loader.load_item()
        else:
            products = hxs.select('.//div[@id="searchResults"]/a')
            if products:
                for product in products:
                    name = product.select('./span[@class="brandName"]/text()').extract()
                    name2 = product.select('./span[@class="productName"]/text()').extract()
                    if name and name2:
                        product_name = name[0].strip() + ' ' + name2[0].strip()
                        product_words = product_name.lower().strip().split(' ')
                        search_words = response.meta['name'].lower().replace('+', ' ').split(' ')
                        diff = [w for w in search_words if not w in product_words]
                        if not diff:
                            price = "".join(product.select('./span[@class="price-6pm"]/text()').re(r'([0-9\,\. ]+)')).strip()
                            loader = ProductLoader(item=Product(), selector=product)
                            loader.add_value('name', product_name)
                            loader.add_value('url', urljoin_rfc(base_url,product.select('.//@href').extract()[0]))
                            loader.add_value('price', price)
                            loader.add_value('sku', response.meta['sku'])
                            if not 'apparelsave' in loader.get_output_value('name').lower():
                                yield loader.load_item()
                                break
