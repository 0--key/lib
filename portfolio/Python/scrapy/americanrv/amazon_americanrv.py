import csv
import os
import copy
import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http.cookies import CookieJar

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class AmazonSpider(BaseSpider):
    name = 'amazon_americanrv.com'
    allowed_domains = ['amazon.com']

    def start_requests(self):
        with open(os.path.join(HERE, 'americanrv_products.csv')) as f:
            reader = csv.reader(f)
            reader.next()
            for row in reader:
                product_ids = set()
                product_ids.add(row[0])
                sku = row[0]
                mfrgid = row[2]
                name = row[1]
                for id in product_ids:
                    query = id.replace(' ', '+')
                    url = 'http://www.amazon.com/s/ref=nb_sb_noss?' + \
                      'url=search-alias%%3Daps&field-keywords=%s&x=0&y=0'

                    yield Request(url % query, meta={'sku': sku, 'mfrgid': mfrgid, 'name': name})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//div[@id="atfResults"]//div[starts-with(@id, "result_")]')
        pr = None
        search_results = []
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', './/h3/a/span/text()')
            if not loader.get_output_value('name'):
                loader.add_xpath('name', './/h3/a/text()')
            loader.add_xpath('url', './/h3/a/@href')
            loader.add_xpath('price', './/ul/li/a/span/text()', re='\$(.*)')
            if not loader.get_output_value('price'):
                loader.add_xpath('price', './/div[@class="newPrice"]//span[contains(@class,"price")]/text()')
            loader.add_value('sku', response.meta['sku'])
            loader.add_value('identifier', response.meta['sku'].lower())
            if loader.get_output_value('price') and (pr is None or pr.get_output_value('price') >
                                                                   loader.get_output_value('price')):
                pr = loader
                search_results.append(pr)

        # if pr:
            # yield pr.load_item()
        if search_results:
            cur_prod = search_results[0]
            next_prods = search_results[1:]
            yield Request(cur_prod.get_output_value('url'), callback=self.parse_mfrgids,
                          meta={'mfrgid': response.meta['mfrgid'], 'name': response.meta['name'], 'cur_prod':cur_prod, 'next_prods':next_prods}, dont_filter=True)

    def parse_mfrgids(self, response):
        hxs = HtmlXPathSelector(response)
        cur_prod = response.meta['cur_prod']
        mfrgid = response.meta['mfrgid']
        keywords = response.meta['name'].split(' ')
        site_mfrgid = hxs.select('//div[@class="tsRow" and child::span[contains(text(),"Manufacturer")]]/span[not(@class)]/text()').extract()
        sub = re.sub
        mfrgid = sub('[-\. ]', '', mfrgid)
        keywords = map(lambda x: sub('[-\. ]', '', x), keywords)
        keywords.append(mfrgid)
        if not site_mfrgid:
            site_mfrgid = hxs.select('//td[@class="techSpecTD2" and preceding-sibling::td[contains(text(),"Manufacturer")]]/text()').extract()
        matched = False
        if site_mfrgid:
            site_mfrgid = site_mfrgid[0]
            for keyword in keywords:
                if keyword in site_mfrgid or site_mfrgid in keyword:
                    matched = True
                    break
        if matched:
            yield cur_prod.load_item()
        else:
            if response.meta['next_prods']:
                cur_prod = response.meta['next_prods'][0]
                yield Request(cur_prod.get_output_value('url'), callback=self.parse_mfrgids,
                      meta={'mfrgid': response.meta['mfrgid'], 'name': response.meta['name'], 'cur_prod':cur_prod, 'next_prods':response.meta['next_prods'][1:]}, dont_filter=True)