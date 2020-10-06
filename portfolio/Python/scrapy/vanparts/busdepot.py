import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class BusDepotSpider(BaseSpider):
    name = 'busdepot.com'
    allowed_domains = ['http://www.busdepot.com', 'www.busdepot.com']
    start_urls = ('http://www.busdepot.com/',)

    def __init__(self, *args, **kwargs):
        super(BusDepotSpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://www.busdepot.com/'

        # parse the csv file to get the product ids
        csv_file = csv.reader(open(os.path.join(HERE, 'monitored_products.csv')))

        self.product_ids = [row[0] for row in csv_file]
        self.product_ids = self.product_ids[1:]
        self.product_ids = [re.sub('[\- \.]', '', product_id) for product_id in self.product_ids]

    def start_requests(self):
        url = 'http://www.busdepot.com'
        yield Request(url, callback=self.search_requests)

    def search_requests(self, response):
        for product_id in self.product_ids:
            form_name = 'search'
            form_data = {'q': product_id}
            form_request = FormRequest.from_response(response, formname=form_name, formdata=form_data, dont_click=True,
                                                     dont_filter=True, priority=1)
            form_request.meta['sku'] = product_id
            yield form_request

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        
        products = hxs.select('//h2[@class="product-name"]/..')
        for product in products:
            try:
                product_loader = ProductLoader(item=Product(), selector=product)
                name = product.select('.//h2/a/text()').extract()[0].strip()
                product_loader.add_value('name', response.meta['sku'].lower())
                price = product.select('.//span[@class="price"]/text()').extract()[0]
                product_loader.add_value('price', price)
                product_loader.add_value('sku', response.meta['sku'])
                url = product.select('.//h2/a/@href').extract()[0].strip()
                prod_id = url.replace(self.URLBASE, '')
                product_loader.add_value('url', self.URLBASE + 'details.jsp?partnumber=' + prod_id.upper())
                yield product_loader.load_item()
            except IndexError:
              continue
            return