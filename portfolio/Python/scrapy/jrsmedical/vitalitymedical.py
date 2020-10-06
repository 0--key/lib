import os
import csv
import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class VitalityMedicalSpider(BaseSpider):
    name = 'vitalitymedical.com'
    allowed_domains = ['vitalitymedical.com']
    start_urls = ()

    def start_requests(self):
        with open(os.path.join(HERE, 'jrsmedical_products.csv')) as f:
            reader = csv.reader(f)
            reader.next()
            reader = set([row[1] for row in reader])
            url = 'http://www.vitalitymedical.com/catalogsearch/result/?q=%s&x=0&y=0'
            for row in reader:
                sku = row
                if url:
                    yield Request(url % re.sub(' ', '+', sku), meta={'sku': sku}, dont_filter=True)


    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # next_page = hxs.select(u'').extract()

        # if next_page:
            # yield Request(urljoin_rfc(base_url, next_page[0]), meta=response.meta)

        products = hxs.select(u'//h5/a/@href').extract()
        for url in products:
            url = urljoin_rfc(base_url, url)
            yield Request(url, callback=self.parse_product, meta=response.meta, dont_filter=True)
        if not products:
            try:
                for product in self.parse_product(response):
                    yield product
            except TypeError:
                pass

    def parse_product(self, response):
        base_url = get_base_url(response)
        search_sku = response.meta['sku']
        hxs = HtmlXPathSelector(response)

        main_name = hxs.select(u'//h3[@class="product-name"]/text()').extract()
        main_price = hxs.select(u'//div[@class="special_price"]//span[@class="price"]').extract()
        if not main_name and not main_price:
            return
        main_name = main_name[0].strip()
        if main_price:
            main_price = main_price[0].strip()
        subproducts = hxs.select(u'//table[@id="super-product-table"]//tr')[1:]
        subproducts += hxs.select(u'//table[@class="inner-table"]//tr')
        if subproducts:
            for p in subproducts:
                product_data = [s.strip() for s in p.select(u'.//td//text()').extract()[:-1] if s.strip() != '']
                loader = ProductLoader(item=Product(), response=response)
                loader.add_value('url', response.url)
                loader.add_value('name', main_name + ' ' + ' '.join(product_data[0:-1]).strip())
                if product_data[-1].startswith('$'):
                    loader.add_value('price', product_data[-1])
                loader.add_value('sku', search_sku)

                sku = product_data[0]
                if sku in search_sku and loader.get_output_value('price'):
                    yield loader.load_item()
