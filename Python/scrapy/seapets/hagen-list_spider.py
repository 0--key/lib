import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.contrib.spiders import CSVFeedSpider

from productloader import load_product
from scrapy.http import FormRequest

class hagenlist_spider(CSVFeedSpider):
    name = 'hagen-list.com'
    allowed_domains = ['competitormonitor.com', 'www.competitormonitor.com']
    start_urls = ('http://competitormonitor.com/users_data/hagen-list_site.txt',)
    
    delimiter = ','
    headers = ['', 'name', 'price']

    def parse_row(self, response, row):
        res = {}
        name = row['name']
        url = ''
        price = row['price']
        res['url'] = url
        res['description'] = name
        res['price'] = price
        return load_product(res, response)