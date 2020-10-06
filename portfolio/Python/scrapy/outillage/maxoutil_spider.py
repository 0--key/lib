import re
import csv
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest


CSV_FILENAME = os.path.join(os.path.dirname(__file__), 'maxoutil.csv')

def normalize_name(name):
    return re.sub(' +', ' ', name).strip().lower()

class maxoutil_spider(BaseSpider):
    name = 'maxoutil.com'
    allowed_domains = ['maxoutil.com', 'www.maxoutil.com']
    start_urls = ('http://www.maxoutil.com/198-outillage-electroportatif',
                  'http://www.maxoutil.com/199-consommables-accessoires-epi',
                  'http://www.maxoutil.com/200-outillage-a-main',
                  'http://www.maxoutil.com/201-fixation',
                  'http://www.maxoutil.com/3403-quincaillerie-de-batiment',
                  'http://www.maxoutil.com/5713-gros-oeuvre-manutention')

    def __init__(self, *args, **kwargs):
        super(maxoutil_spider, self).__init__(*args, **kwargs)
        self.names = {}
        with open(CSV_FILENAME) as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.names[normalize_name(row['name'])] = row['name']

    def parse_product(self, response):
        
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//ul[@id="product_list"]/li')
        cnt = 0
        for p in products:
            res = {}
            try:
                name = p.select('.//h3/a/@title').extract()[0]
                name = normalize_name(name)
                name = self.names.get(name, name)
            except Exception:
                continue
	      
            url = p.select('.//h3/a/@href').extract()[0]
            price = p.select('.//span[@class="price"]/text()').re(r'([0-9\.\, ]+)')[0]
            res['url'] = url
            res['description'] = name
            res['price'] = price
            yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)
        next_page = hxs.select('//li[@id="pagination_next"]/a/@href').extract()
        if next_page:
            yield Request(urljoin_rfc(get_base_url(response), next_page[0]))

        # products
        for p in self.parse_product(response):
            yield p