import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class BeautyEncounterSpider(BaseSpider):
    name = 'beautyencounter.com'
    allowed_domains = ['beautyencounter.com']
    #start_urls = ('http://www.beautyencounter.com/',)
    #start_urls = ('http://www.beautyencounter.com/discount/perfumes-and-colognes/4',)

    def start_requests(self):
        with open(os.path.join(HERE, 'beauty.txt')) as f:
            for url in f:
                yield Request(url.strip())

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        loader = ProductLoader(item=Product(), response=response)
        loader.add_xpath('name', '//h1[@itemprop="name"]/text()')
        loader.add_xpath('price', '//*[@itemprop="price"]/text()')
        loader.add_value('url', response.url)

        yield loader.load_item()

