import re
import os
import csv
import hashlib

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


class AbelandColeSpider(BaseSpider):

    name = 'abelandcole.co.uk'
    allowed_domains = ['www.abelandcole.co.uk', 'abelandcole.co.uk']
    start_urls = ('http://www.abelandcole.co.uk/fruit-veg?so=5',
                  'http://www.abelandcole.co.uk/meat/chicken-duck?so=5',
                  'http://www.abelandcole.co.uk/meat/beef?so=5',
                  'http://www.abelandcole.co.uk/meat/pork?so=5',
                  'http://www.abelandcole.co.uk/meat/lamb?so=5',
                  'http://www.abelandcole.co.uk/meat/sausages-bacon-burgers?so=5',
                  'http://www.abelandcole.co.uk/meat/meat-boxes?so=5',
                  'http://www.abelandcole.co.uk/meat/mince?so=5',
                  'http://www.abelandcole.co.uk/meat/offal?so=5')

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # getting product details from product list
        prod_names = hxs.select('//h4/a/@title').extract()
        prod_urls = hxs.select('//h4/a/@href').extract()
        prices = hxs.select('//td[@class="ProductPrice"]/h4/text()').extract()
        prices = [p.strip().strip(u'\xa3') for p in prices]
        
        names_urls_prices = zip(prod_names, prod_urls, prices)
        for name, url, price in names_urls_prices:
            url = urljoin_rfc(get_base_url(response), url)
            if url:
                loader = ProductLoader(item=Product(), selector=hxs)
                loader.add_value('url', url)
                loader.add_value('name', name)
                loader.add_value('price', price)
                yield loader.load_item()

        # pages
        next_page = hxs.select('//a[@class="NextPage"]/@href').extract()
        if next_page:
            url = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(url)