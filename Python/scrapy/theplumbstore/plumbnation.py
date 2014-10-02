import re
import os
import csv
import hashlib
import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
from product_spiders.items import Product, ProductLoaderWithNameStrip\
                             as ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))


class PlumbNationSpider(BaseSpider):

    name = 'plumbnation.co.uk'
    allowed_domains = ['www.plumbnation.co.uk', 'plumbnation.co.uk']
    start_urls = ('http://www.plumbnation.co.uk/', 'http://www.plumbnation.co.uk/shop-by-brand.php')

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        urls = hxs.select('//ul[@class="navVertical"]/li/a/@href').extract()
        for url in urls:
            url = urljoin_rfc(get_base_url(response), url)
            request = Request(url, callback=self.parse_product_list)
            yield request

#        urls = hxs.select('//div[@class="manufacturers"]//ul[@class="navVertical"]/li/a/@href').extract()
#        for url in urls:
#            url = urljoin_rfc(get_base_url(response), url)
#            request = Request(url, callback=self.parse_product_list)
#            yield request

        # pages
        #next_page = hxs.select('//a[@class="next_page page_num"]/@href').extract()
        #if next_page:
        #    url = urljoin_rfc(get_base_url(response), next_page[0])
        #    yield Request(url)

    def parse_product_list(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        cat_urls = hxs.select('//ul[contains(@class, "categories")]/li//a/@href').extract()
        for url in cat_urls:
            url = urljoin_rfc(get_base_url(response), url)
            request = Request(url, callback=self.parse_product_list)
            yield request

        prod_urls = hxs.select('//ul[contains(@class, "products")]/li//span[contains(@class, "name")]/a/@href').extract()
        for url in prod_urls:
            url = urljoin_rfc(get_base_url(response), url)
            request = Request(url, callback=self.parse_product)
            yield request

        urls = hxs.select('//div[@class="pagination"]//ul[@class="navHorizontal"]/li/a/@href').extract()
        for url in urls:
            url = urljoin_rfc(get_base_url(response), url)
            request = Request(url, callback=self.parse_product_list)
            yield request

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        prod_name = hxs.select('//div[@id="productSpecification"]/div/table/tr[1]/td[2]/text()').extract()
        if prod_name:
            mpn = ''.join(hxs.select('//*[@id="productSpecification"]/div/table/tr[td/text()="Manufacturer Code"]/td[@class="productAttributeValue"]/text()').extract())
            url = response.url
            url = urljoin_rfc(get_base_url(response), url)
            
            loader = ProductLoader(item=Product(), selector=hxs)
            loader.add_value('url', url)
            #if not mpn in prod_name[0]:
            #    loader.add_value('name', ' '.join((prod_name[0], mpn)))
            #else:
            #    loader.add_value('name', prod_name[0])
            loader.add_value('name', prod_name[0])
            sku = hxs.select('//div[@id="productSpecification"]/div/table/tr[2]/td[2]/text()').extract()
            if sku:
                loader.add_value('sku', sku[0])
                loader.add_value('identifier', sku[0])
            price = ''.join(hxs.select('//div[@id="productAddToCart"]/div/b/text()').extract())
            if price:
                loader.add_value('price', price)
            yield loader.load_item()
        else:
            # several productSpecification
            prods = hxs.select('//div[@class="productInformation"]')
            for prod in prods:
                mpn = ''.join([code for code in prod.select('p/text()').extract() if 'Manufacturer Code' in code]).strip().split(':')[-1]
                url = prod.select('./a/@href').extract()
                url = urljoin_rfc(get_base_url(response), url[0])
                if url:
                    loader = ProductLoader(item=Product(), selector=hxs)
                    loader.add_value('url', url)
                    
                    name = prod.select('./a/text()').extract()
                    if name:
                        if not mpn in name[0]:
                            loader.add_value('name', ' '.join((name[0], mpn)))
                        else:
                            loader.add_value('name', name[0])
                        #loader.add_value('name', name[0])
                    
                    sku = prod.select('./p[1]').extract()
                    if sku:
                        match = re.search('(\d+)', sku[0])
                        sku = match.group(1)
                        loader.add_value('sku', sku)
                        loader.add_value('identifier', sku) 

                    price = ''.join(prod.select('./p/b/text()').extract()).split('(')[0]
                    if price:
                        loader.add_value('price', price)
                    yield loader.load_item()
