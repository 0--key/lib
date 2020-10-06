import os
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.fuzzywuzzy import process
from product_spiders.fuzzywuzzy import fuzz

HERE = os.path.abspath(os.path.dirname(__file__))

class EbaySpider(BaseSpider):
    name = 'portclewaquatics-ebay.co.uk'
    allowed_domains = ['ebay.co.uk']
    start_urls = ['http://stores.ebay.co.uk/Portclew-Aquatics']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//table[@class="grid"]/tr/td')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'table/tr/td/div[@class="ttl g-std"]/a/@title')
            loader.add_xpath('url', 'table/tr/td/div[@class="ttl g-std"]/a/@href')
            loader.add_xpath('price', 'table/tr/td/div/table/tr/td/span[@itemprop="price"]/text()')
            yield loader.load_item()
        next = hxs.select('//td[@class="next"]/a/@href').extract()
        if next:
            url =  urljoin_rfc(get_base_url(response), next[0])
            yield Request(url)
