import re
import os
import random

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.spiders.BeautifulSoup import BeautifulSoup

import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class RVPartsCenterSpider(BaseSpider):
    name = 'rvpartscenter_americanrv.com'
    allowed_domains = ['www.rvpartsscenter.com']
    start_urls = ('http://www.rvpartscenter.com/',)
    user_agent = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; Media Center PC 6.0; InfoPath.2; MS-RTC LM 8)'
    #download_delay = 5

    def __init__(self, *args, **kwargs):
        super(RVPartsCenterSpider, self).__init__(*args, **kwargs)
        self.user_agents = []
        with open(os.path.join(HERE, 'user_agents.txt')) as f:
            for agent in f:
                self.user_agents.append(agent)

        csv_file = csv.reader(open(os.path.join(HERE, 'americanrv_products.csv')))
        csv_file.next()
        self.product_ids = {}
        for row in csv_file:
            ids = row[3].split(' ')
            ids = filter(lambda x: x != '', ids)
            # remove all year ranges
            regexp = re.compile('^[0-9]{2}-[0-9]{2}$')
            ids = filter(lambda x: not regexp.match(x), ids)
            ids.append(row[2])
            self.product_ids[row[0]] = {'mfrgid': row[2], 'ids': frozenset(ids)}

    def start_requests(self):
        existing_products = []
        with open(os.path.join(HERE, 'rvpartsproducts.csv')) as f:
            reader = csv.reader(f)
            reader.next()
            for row in reader:
                existing_products.append(row[0])

        for sku, data in self.product_ids.items():
            if sku.lower() not in existing_products:
                continue

            for id in data['ids']:
                url = 'http://www.rvpartscenter.com/FindaProduct.asp?ProdD=' + re.sub(' ','+', id) + '&x=0&y=0'
                req = Request(url, callback=self.parse)
                req.meta['sku'] = sku
                req.meta['mfrgid'] = data['mfrgid']
                req.meta['search_q'] = id
                #req.headers['User-Agent'] = 'codebldi'#random.choice(self.user_agents)
                yield req
            
    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # pagination
        # next_page = hxs.select(u'//a[child::font[contains(text(),"Next")]]/@href').extract()
        # if next_page:
            # next_page = urljoin_rfc(get_base_url(response), next_page[0])
            # yield Request(next_page)

        # products
        for product in self.parse_product(response):
            yield product

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)
        soup = BeautifulSoup(response.body)

        products = soup.findAll('a', href=re.compile('ProductDetail'))
        products = {product.parent.parent for product in products}

        for product in products:
            product_loader = ProductLoader(item=Product(), response=response)
            name = product.findAll('font')[1].text
            price = product.find('nobr', text=re.compile('\$'))
            url = product.find('a', href=re.compile('ProductDetail'))
            if url:
                url = urljoin_rfc(get_base_url(response), url['href'])
            else:
                url = response.url
            product_loader.add_value('name', name)
            product_loader.add_value('price', price)
            product_loader.add_value('url', url)
            product_loader.add_value('url', url)
            product_loader.add_value('sku', response.meta['sku'])
            #product_loader.add_value('identifier', response.meta['sku'])
            site_mfrgid = product.find('nobr').text
            if site_mfrgid:
                site_mfrgid = site_mfrgid.strip().lower()
                mfrgid = response.meta['mfrgid'].strip().lower()
                if site_mfrgid == mfrgid:
                    yield product_loader.load_item()
