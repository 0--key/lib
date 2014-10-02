import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy import log

import csv, codecs, cStringIO

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class PplmotorhomesSpider(BaseSpider):
    USER_AGENT = "Googlebot/2.1 ( http://www.google.com/bot.html)"
    name = 'pplmotorhomes_americanrv.com'
    allowed_domains = ['www.pplmotorhomes.com','pplmotorhomes.com','google.com','www.google.com']
    start_urls = ('http://www.google.com',)

    def __init__(self, *args, **kwargs):
        super(PplmotorhomesSpider, self).__init__(*args, **kwargs)
        # parse the csv file to get the product ids
        csv_file = csv.reader(open(os.path.join(HERE, 'americanrv_products.csv')))
        csv_file.next()
        self.product_ids = {}
        for row in csv_file:
            ids = row[3].split(' ')
            if ids[0] == '':
                ids = set()
            else:
                ids = set(ids)
            ids.add(row[0])
            ids.add(row[2])
            self.product_ids[row[0]] = {'ids': frozenset(ids), 'mfrgid': row[2]}

    def start_requests(self):

        for sku, data in self.product_ids.items():
            for id in data['ids']:
                url = 'http://www.google.com/cse?cx=008536649155685395941%3Aiahjfr-bdbs&ie=UTF-8&q='+re.sub(' ','+', id)+'&sa=Search&siteurl=www.pplmotorhomes.com&ref=www.pplmotorhomes.com&nojs=1'
                req = Request(url, callback=self.parse)
                req.meta['search_q'] = id
                req.meta['sku'] = sku
                req.meta['mfrgid'] = data['mfrgid']
                yield req

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        product_urls = hxs.select('//a[@class="l"]/@href').extract()
        #product_urls = hxs.select('//a[@class="gs-title"]/@href').extract()
        #log.msg("CRAWLING:::::::::::  %s" % hxs.select('/html').extract())
        if product_urls:
            request = Request(product_urls[0], callback=self.parse_product, dont_filter=True)
            request.meta['sku'] = response.meta['sku']
            request.meta['search_q'] = response.meta['search_q']
            request.meta['mfrgid'] = response.meta['mfrgid']
            yield request
        else:
            return


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        
        products = hxs.select('//table[@width="86%"]/tr')
        for product in products:
            sku_ = product.select('./form/td[1]/b/text()').extract()
            if sku_:
              site_mfrgid = product.select('./form/td[2]/font[contains(text(),"Manufacturer")]/b/text()').extract()
              if site_mfrgid:
                  site_mfrgid = site_mfrgid[0].lower() == response.meta['mfrgid'].lower()
              else:
                  site_mfrgid = False
              if sku_[0] == response.meta['search_q'] or site_mfrgid:
                price = "".join(product.select("./form/td[3]/font/b/text()").re(r'([0-9\,\. ]+)')).strip()
                if price:
                    name = product.select('./form/td[2]/text()').extract()[0]
                    product_loader = ProductLoader(item=Product(), response=response)
                    if '...Regularly' in name:
                        name = re.sub('\.{3}Regularly.*?\$.*$', '', name)
                    product_loader.add_value('price', price)
                    product_loader.add_value('url', response.url)
                    product_loader.add_value('sku', response.meta['sku'])
                    product_loader.add_value('identifier', response.meta['sku'].lower())
                    product_loader.add_value('name', response.meta['sku'] + ' '  + name)
                    yield product_loader.load_item()
        name = hxs.select(u'//h1[@class="big product_title"]/text()').extract()
        if not products and name:
            product_loader = ProductLoader(item=Product(), response=response)
            name = name[0]
            if '...Regularly' in name:
                name = re.sub('\.{3}Regularly.*?\$.*$', '', name)
            product_loader.add_value('name', name)
            product_loader.add_xpath('price', u'//dt[@id="prod_price"]//span[@class="small"]/strong[@class="big"]/text()',
                                    re='\$(.*)')
            product_loader.add_value('sku', response.meta['sku'])
            product_loader.add_value('identifier', response.meta['sku'].lower())
            product_loader.add_value('url', response.url)
            site_mfrgid = hxs.select(u'//span[@class="small" and contains(text(),"Manufacturer")]/following-sibling::strong[1]/text()').extract()
            if site_mfrgid:
                site_mfrgid = site_mfrgid[0].lower().strip()
                if site_mfrgid == response.meta['mfrgid'].strip().lower():
                    yield product_loader.load_item()