import os
import csv
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class FoneBankSpider(BaseSpider):
    name = 'fonebank.com'
    allowed_domains = ['fonebank.com']

    def __init__(self, *args, **kwargs):
        super(FoneBankSpider, self).__init__(*args, **kwargs)
        csv_file = csv.reader(open(os.path.join(HERE, 'fonebank_products.csv')))
        self.products =[(row[0], row[1]) for row in csv_file]

    def start_requests(self):
        for name, url in self.products:
	    name = name.strip()
            yield Request(url)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        status = hxs.select('//*[@id="ctl00_ContentPlaceHolder1_div_working"]')
        loader = ProductLoader(item=Product(), selector=status)
        name = ' '.join(status.select('table/tr/td/span[@id="ctl00_ContentPlaceHolder1_lblmodelname"]/text()').extract())
        loader.add_value('name', ' '.join((name, 'Working')))
        loader.add_value('url', response.url)
        loader.add_xpath('price', 'table/tr/td/div/span[@id="ctl00_ContentPlaceHolder1_lblprice"]/text()')
        yield loader.load_item()
        status = hxs.select('//*[@id="ctl00_ContentPlaceHolder1_div_not_working"]')
        loader = ProductLoader(item=Product(), selector=status)
        name = status.select('table/tr/td/span[@id="ctl00_ContentPlaceHolder1_lblnonworkingmodelname"]/text()').extract()[0]
        loader.add_value('name', ' '.join((name, 'Not working')))
        loader.add_value('url', response.url)
        loader.add_xpath('price', 'table/tr/td/div/span[@id="ctl00_ContentPlaceHolder1_lblpricenonworking"]/text()')
        yield loader.load_item()
        

