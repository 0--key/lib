import os
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url
import re

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.fuzzywuzzy import process
from product_spiders.fuzzywuzzy import fuzz

HERE = os.path.abspath(os.path.dirname(__file__))

class CharterhouseAquaticsSpider(BaseSpider):
    name = 'charterhouse-aquatics.co.uk'
    allowed_domains = ['charterhouse-aquatics.co.uk']
    start_urls = ['http://www.charterhouse-aquatics.co.uk/']
    brand_crawled = False

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        categories = hxs.select('//ul[@class="nav"]//a/@href').extract()
        for url in categories:
            if not re.search('^http', url):
                url = urljoin_rfc(base_url, url)
            yield Request(url, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)

        if not self.brand_crawled:
            brands = hxs.select('//*[@class="infoBox-categories"]//a/@href').extract()
            for url in brands:
                if not re.search('^http', url):
                    url = urljoin_rfc(base_url, url)
                yield Request(url, callback=self.parse_products)
            self.brand_crawled = True

        # Is it another subcategory page?
        sub_sub_categories = hxs.select('//div[@id="catView"]//a/@href').extract()
        for url in sub_sub_categories:
            if not re.search('^http', url):
                url = urljoin_rfc(base_url, url)
            yield Request(url, callback=self.parse_products)

        # Is it products page?
        products = hxs.select('//div[@id="productView"]/ul/li[@class="product"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', './/h2/a/text()')
            loader.add_xpath('price', './/h3/a/text()')
            loader.add_xpath('url', './/h2/a/@href')
            yield loader.load_item()
