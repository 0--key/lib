import os
import csv
import string
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url
from product_spiders.fuzzywuzzy import process

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class SimplyElectronicsSpider(BaseSpider):
    name = 'simplyelectronics.net'
    allowed_domains = ['simplyelectronics.net']
    start_urls = ['http://www.simplyelectronics.net/sitemap.php']

    def parse(self, response):
       
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//a[@class="moreinfo"]/@href').extract()
        for category in categories:
            url = urljoin_rfc(get_base_url(response), category)
            yield Request(url+'&currency=pound', callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//table[@width="100%" and @cellspacing="0" and @cellpadding="4" and @border="0"]/tr/td/table[@width="100%" and @border="0"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'tr/td/a/b/text()')
            url = urljoin_rfc(get_base_url(response), product.select('tr/td/a[@class="blacklink"]/@href').extract()[0])
            loader.add_value('url', url)
            loader.add_xpath('price', 'tr/td/b/text()')
            yield loader.load_item()
