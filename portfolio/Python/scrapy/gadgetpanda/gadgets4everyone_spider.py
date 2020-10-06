import re
import csv
import os
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

from scrapy import log
from scrapy.conf import settings

settings.overrides['DOWNLOAD_DELAY'] = 2

HERE = os.path.abspath(os.path.dirname(__file__))

class Gadgets4EveryoneSpider(BaseSpider):
    name = 'gadgets4everyone.co.uk'
    allowed_domains = ['gadgets4everyone.co.uk']

    def __init__(self, *args, **kwargs):
        super(Gadgets4EveryoneSpider, self).__init__(*args, **kwargs)
        csv_file = csv.reader(open(os.path.join(HERE, 'gadgets4everyone_products.csv')))
        self.products = [row[1] for row in csv_file]

    def start_requests(self):
        for url in self.products:
            yield Request(url)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        deduct = self.get_data(hxs.extract(), 'productDeduc.push("','")')
        answers = self.get_data(hxs.extract(), 'productAns.push("','")')
        checks = hxs.select('//form[@name="customVal"]/table/tr/td[@style="padding-left:30px;"]/text()').extract()
        answers_deduct = zip(answers, deduct)
        options = zip(checks, answers_deduct)
        #Gets the prices.
        prices = zip(['Like New', 'Fair', 'Poor'], self.get_data(hxs.extract(), 'pp1=',';\n')[:-1])
        for grade, price in prices:
            loader = ProductLoader(item=Product(), response=response)
            name = hxs.select('//*[@id="vmMainPage"]/div/div/div/div/h1/text()').extract()[0]
            loader.add_value('name', ' '.join((name, grade)))
            loader.add_value('price', self.calc_price(float(price), options))
            loader.add_value('url', response.url)
            yield loader.load_item()

    def calc_price(self, ini_price, options):
        value = ini_price
        conditions = ('Fully Working With No Major Faults?',
                      'Fully Working?',
                      'Fully Working With No Faults?',
                      'Fully Working With No Major Faults Or Water Damage?',
                      'Fully Working With No Major Faults (battery Life Excluded)?',
                      'Fully Working With No Major Faults? Charger? SIM Unlocked?')
        for name, option in options:
            if not name.strip() in conditions:
                if option[0]=='no':
                    value = value - ((value * float(option[1]))/100)
        num = str(((abs(value) + .005)*100)/100).split('.')
        return ''.join((num[0],'.', num[1][:2]))

    #Gets the values between two strings
    def get_data(self, url_data, tag_begin, tag_end):
        start = url_data.find(tag_begin)
        end = url_data.find(tag_end, start)
        data = []
        while True:
            data.append(url_data[start+len(tag_begin):end])
            start = url_data.find(tag_begin, end)
            if start>-1:
                end = url_data.find(tag_end, start)
                if end==-1:
                    break
            else:
                break
        return data
