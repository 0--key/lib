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

class shoestealSpider(BaseSpider):
    name = 'shoesteal.com'
    allowed_domains = ['shoesteal.com','www.shoesteal.com']

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
                brand = ""
                style = ""
                query = row['name'].replace(' ', '+')
                url = 'http://www.shoesteal.com/Shopping/Results.aspx?Ntt=' + query + '&x=0&y=0&N=0&Ntk=SearchInterface&Nty=1&Ntx=mode%2Bmatchallany'
                yield Request(url, meta={'sku': sku, 'name': row['name'], 'brand': brand, 'style': style})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)
        products = hxs.select('//div[@class="productCellWrapper"]')
        if not products:
            return
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            brand = "".join(product.select('.//div[@class="productBrandTitleColor"]/a/span[@class="brand"]/text()').extract()).strip()
            style = "".join(product.select('.//div[@class="productBrandTitleColor"]/a/span[@class="styleName color"]/text()').extract()).strip()
            name = "".join(product.select('.//div[@class="productBrandTitleColor"]/a/span[@class="styleName name"]/text()').extract()).strip()
            name = brand + ' ' + name + ' ' + style
            product_words = name.lower().split(' ')
            search_words = response.meta['name'].lower().split()
            diff = [w for w in search_words if not w in product_words]
            if not diff:
                url = product.select('.//div[@class="productBrandTitleColor"]/a/@href').extract()[0]
                price = "".join(product.select('.//div[@class="price"]/span[@class="salePrice"]/text()').re(r'([0-9\,\. ]+)')).strip()
                if not price:
                    price = "".join(product.select('.//div[@class="price"]/text()').re(r'([0-9\,\. ]+)')).strip()
                loader.add_value('name', name)
                loader.add_value('url', urljoin_rfc(base_url,url))
                loader.add_value('price', price)
                loader.add_value('sku', response.meta['sku'])

                if not 'apparelsave' in loader.get_output_value('name').lower():
                    yield loader.load_item()
                    break
            """
            name = "".join(product.select('.//div[@class="productBrandTitleColor"]/a/span[@class="brandName"]/text()').extract()).strip()
            if name and response.meta['brand'].lower() in name.lower():
                name2 = "".join(product.select('.//div[@class="productBrandTitleColor"]/a/span[@class="styleName"]/text()').extract()).strip()
                #log.msg('NAME2: ' + self.words_replace(name2) + ' ---- ORIG: ' + response.meta['style'].lower())
                if name2 and response.meta['style'].lower() == self.words_replace(name2):
                    url = product.select('.//div[@class="productBrandTitleColor"]/a/@href').extract()[0]
                    price = "".join(product.select('.//div[@class="productPrice"]/span[@class="variantSalePrice"]/text()').re(r'([0-9\,\. ]+)')).strip()
                    if not price:
                        price = "".join(product.select('.//div[@class="productPrice"]/text()').re(r'([0-9\,\. ]+)')).strip()
                    loader.add_value('name', name + ' ' + name2)
                    loader.add_value('url', urljoin_rfc(base_url,url))
                    loader.add_value('price', price)
                    loader.add_value('sku', response.meta['sku'])

                    if not 'apparelsave' in loader.get_output_value('name').lower():
                        yield loader.load_item()
                        break"""

    def words_replace(self, s):
        patterns = ["Men's", "Women's", "Kids'", "Girl's", "Boy's", 'Unisex']
        for pattern in patterns:
            s = s.replace(pattern,'');
        return s.strip().lower()

