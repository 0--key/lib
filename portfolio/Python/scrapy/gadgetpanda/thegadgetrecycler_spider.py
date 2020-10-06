import os
import csv
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from product_spiders.fuzzywuzzy import process

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class GadgetRecyclerSpider(BaseSpider):
    name = 'thegadgetrecycler.com'
    allowed_domains = ['thegadgetrecycler.com']

    def __init__(self, *args, **kwargs):
        super(GadgetRecyclerSpider, self).__init__(*args, **kwargs)
        csv_file = csv.reader(open(os.path.join(HERE, 'thegadgetrecycler_products.csv')))
        self.products =[(row[0], row[1]) for row in csv_file]

    def start_requests(self):
        for name, url in self.products:
	    name = name.strip()
            if url:
                yield Request(url, meta={'name':name})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        prices = hxs.select('//*[@id="show-price"]/div/h2/span/text()').extract()
        if prices:
            grades = ['Grade A','Grade B','Grade C','Grade D','Grade E']
            prod_prices = dict(zip(grades,prices))
            for grade, price in prod_prices.iteritems():
                loader = ProductLoader(item=Product(), response=response)
                loader.add_value('name', ' '.join((response.meta['name'],grade)))
                loader.add_value('url', response.url)
                loader.add_value('price', price)
                yield loader.load_item()
       
