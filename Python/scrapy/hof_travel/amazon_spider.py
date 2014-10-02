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

#from ignore_words import accept_product

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.spiders.BeautifulSoup import BeautifulSoup

from pricecheck import valid_price

HERE = os.path.abspath(os.path.dirname(__file__))

class AmazonSpider(BaseSpider):
    name = 'houseoffraser-travel-amazon.com'
    allowed_domains = ['amazon.com']
    user_agent = 'spd'

    def start_requests(self):
        shutil.copy(os.path.join(HERE, 'houseoffraser_travel.csv'),os.path.join(HERE, 'houseoffraser_travel.csv.' + self.name + '.cur'))
        with open(os.path.join(HERE, 'houseoffraser_travel.csv.' + self.name + '.cur')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                #sku = row['sku']
                """
                brand = row['brand']
                style = row['style']
                query = (brand + ' ' + style).replace(' ', '+')
                """
                query = row['name'].replace(' ','+')
                url = 'http://www.amazon.co.uk/s/ref=nb_sb_noss?' + \
                      'url=search-alias%%3Daps&field-keywords=%(q)s&x=0&y=0'

                yield Request(url % {'q': query}, meta={'price': row['price'].replace('$', '')})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//div[@id="atfResults"]//div[starts-with(@id, "result_")]')
        pr = None
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)

            soup = BeautifulSoup(product.extract())
            loader.add_value('name', soup.find('h3', attrs={'class': 'newaps'}).findAll('span')[0].string)
            loader.add_value('url', soup.find('h3', attrs={'class': 'newaps'}).findAll('a')[0]['href'])
            loader.add_value('price', soup.find('ul', attrs={'class': 'rsltL'}).findAll('span')[0].string)
            #loader.add_value('sku', response.meta['sku'])
            #loader.add_value('identifier', response.meta['sku'])

            if loader.get_output_value('price') and (pr is None or pr.get_output_value('price') >
                                                                   loader.get_output_value('price')) and \
               valid_price(response.meta['price'], loader.get_output_value('price')):
                pr = loader

        if pr:
            yield pr.load_item()
