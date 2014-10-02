import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
import hashlib

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class OfficeSpotSpider(BaseSpider):
    name = 'officespot.ie'
    allowed_domains = ['www.officespot.ie', 'officespot.ie']
    start_urls = ('http://www.officespot.ie/brands/',
                  'http://www.officespot.ie/catalog/seo_sitemap/category/')

    def __init__(self, *args, **kwargs):
        super(OfficeSpotSpider, self).__init__(*args, **kwargs)
        self.skus = []
        with open(os.path.join(HERE, 'officespot_skus.csv'), 'rb') as f:
            reader = csv.reader(f)
            self.skus = tuple([row[1] for row in reader])

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # brands
        brands = hxs.select(u'//ul[@class="bare-list"]//a/@href').extract()
        for url in brands:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # categories
        categories = hxs.select(u'//li[contains(@class,"level-0")]/a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # subcategories
        subcategories = hxs.select(u'//div[@class="fieldset-custom" and descendant::h2[text()="Categories"]]//div[@class="cat_name"]//a/@href').extract()
        for url in subcategories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pagination
        next_page = hxs.select(u'//a[@class="next" and @title="Next" and contains(text(), "Next")]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        # products
        for product in self.parse_product(response):
            yield product
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        products = hxs.select(u'//ol[@id="products-list" and @class="products-list"]//li[contains(@class,"item")]')
        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//h2[@class="product-name"]/a/@href').extract()
            url = urljoin_rfc(get_base_url(response), url[0])
            product_loader.add_value('url', url)
            sku = product.select(u'.//small[child::b[contains(text(),"Product Code:")]]/text()').extract()
            if sku:
                sku = sku[0].strip()[3:]
            if sku in self.skus:
                product_loader.add_value('sku', sku)
            name = product.select(u'.//h2[@class="product-name"]/a/text()').extract()[0].strip()
            pack_size = product.select(u'.//small[child::b[contains(text(),"Pack Size:")]]/text()').extract()
            if pack_size:
                name += u' x' + pack_size[0].strip() + u'u.'
            product_loader.add_value('name', name)
            price = product.select(u'.//div[@class="price-box"]/span[contains(@class,"regular-price")]/span[@class="price"]/text()').re(u'[\d\.,]+')
            price = re.sub(',', '', price[0])
            product_loader.add_value('price', price)
            yield product_loader.load_item()