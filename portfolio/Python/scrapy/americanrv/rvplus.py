import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class RVPlusSpider(BaseSpider):
    name = 'rvplus.com'
    allowed_domains = ['www.rvplus.com']
    start_urls = ('http://www.rvplus.com/',)

    def __init__(self, *args, **kwargs):
        super(RVPlusSpider, self).__init__(*args, **kwargs)

        csv_file = csv.reader(open(os.path.join(HERE, 'americanrv_products.csv')))
        csv_file.next()
        self.product_ids = {}
        for row in csv_file:
            ids = set()
            ids.add(row[0])
            ids.add(row[2])
            self.product_ids[row[0]] = {'mfrgid': row[2], 'ids': frozenset(ids)}


    def start_requests(self):
        for sku, data in self.product_ids.items():
            for id in data['ids']:
                url = 'http://www.rvplus.com/?subcats=Y&status=A&pshort=Y&pfull=Y&pname=Y&pkeywords=Y&search_performed=Y&cid=0&q=' + re.sub(' ','+', id) + \
                   '&x=0&y=0&dispatch=products.search'
                req = Request(url, meta={'sku': sku, 'mfrgid': data['mfrgid']})
                yield req

            
    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # pagination
        # next_pages = hxs.select(u'//div[@class="pagination cm-pagination-wraper center" and position()=1]//a/@href').extract()
        # for page in next_pages:
        #     page = urljoin_rfc(get_base_url(response), page)
        #     yield Request(page)

        # products
        product_urls = hxs.select(u'//div[@class="product-info"]//a[@class="product-title"]/@href').extract()
        for url in product_urls:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product, dont_filter=True,
                          meta={'mfrgid': response.meta['mfrgid'], 'sku': response.meta['sku']})

        try:
            for product in self.parse_product(response):
                yield product
        except TypeError:
            pass



    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        product_loader = ProductLoader(item=Product(), response=response)
        product_loader.add_xpath('price', u'//span[@class="price"]/span[@class="price" and contains(@id, "sec_discounted_price")]/text()')
        product_loader.add_value('url', response.url)
        product_loader.add_value('sku', response.meta['sku'])
        product_loader.add_value('identifier', response.meta['sku'].lower())
        product_loader.add_xpath('name', u'//div[@class="product-info"]/h1[@class="mainbox-title"]/text()')
        site_mfrgid = hxs.select(u'//div[@class="form-field" and child::label[contains(text(),"Model#")]]/text()').extract()
        if len(site_mfrgid) > 1:
            site_mfrgid = site_mfrgid[1].strip()
            if site_mfrgid == response.meta['mfrgid']:
                yield product_loader.load_item()