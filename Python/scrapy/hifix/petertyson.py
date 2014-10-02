import re
import os
from urllib import urlencode, unquote

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv
import math
import random

from product_spiders.items import Product, ProductLoader


class PeterTysonSpider(BaseSpider):
    name = 'petertyson.co.uk'
    allowed_domains = ['www.petertyson.co.uk', 'www.moltengold.com']
    start_urls = ('http://www.petertyson.co.uk/',)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//ul[@id="MenuBar1"]/li/a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # subcategories
        subcategories = hxs.select(u'//table[@class="TextListingTable"]//a/@href').extract()
        for url in subcategories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pages
        # next_pages = hxs.select(u'').extract()
        # for next_page in next_pages:
            # url = urljoin_rfc(get_base_url(response), next_page)
            # yield Request(url)

        # products
        products = hxs.select(u'//table[@class="ListingTable"]//a/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        name = hxs.select(u'//div[@id="ListingHeading"]/h1/text()').extract()
        url = response.url
        # price retrieval
        eBtrolley = str(math.floor(900000 * random.random()) + 100000).split('.')[0]
        page = response.url
        eBshopcode = '7942PeterTyso'
        eBparam = ''
        eBbottoms = re.search('var eBbottoms="(.*)"', response.body).groups()[0]
        eBsingles = re.search('var eBsingles="(.*)"', response.body).groups()[0]
        eBtops = re.search('var eBtops="(.*)"', response.body).groups()[0]
        eBmids = re.search('var eBmids="(.*)"', response.body).groups()[0]
        url = 'http://www.moltengold.com/cgi-bin/eButtonz61.js'

        params = {'trolley': eBtrolley, 'page': page, 'shop': eBshopcode,
                  'param': eBparam, 'bottoms': eBbottoms, 'singles': eBsingles,
                  'tops': eBtops, 'mids': eBmids}

        url = url + '?' + '&'.join(['%s=%s' % (key, params[key]) for key in params])
        req = Request(url, callback=self._get_prices)
        req.meta['main_response'] = response
        req.meta['hxs'] = hxs
        yield req


    def _get_prices(self, price_response):
        unpriced = re.search('eBunpriced="(.*)"', price_response.body)
        if unpriced:
            unpriced = [prod_id for prod_id in unpriced.groups()[0].split(',') if prod_id.strip()]

        eBzp = [None] * 200
        eBzpp = [None] * 200
        eBzp_assignments = re.findall('(eBzp\[\d+\]=.*);', price_response.body)
        for assignment in eBzp_assignments:
            exec assignment.replace('eBop', "''").replace('eBspl', "'&'").replace('eBsp', "'&'")

        eBzpp_assignments = re.findall('(eBzpp\[\d+\]=.*);', price_response.body)
        for assignment in eBzpp_assignments:
            exec assignment.replace('eBop', "'&'").replace('eBspl', "'&'").replace('eBsp', "'&'")

        prices = {}

        for i, prod in enumerate(eBzp):
            if prod:
                prices[prod] = eBzpp[i]

        hxs = price_response.meta['hxs']
        main_name = hxs.select('//h1/text()').extract()[0].strip()

        products = hxs.select('//form[@id="eBvariant1"]//option')
        subprods = hxs.select('//div[@id="TabbedPanels1"]//em/strong[contains(text(), "//")]/text()').extract()

        if not products and subprods:
            subprods = subprods[0].split('//')
            for prod in subprods:
                r = prod.split(':')
                if len(r) == 2:
                    p = Product()
                    loader = ProductLoader(response=price_response.meta['main_response'], item=p)
                    loader.add_value('name', main_name + ' ' + r[0].strip())
                    loader.add_value('price', r[1])
                    loader.add_value('url', price_response.meta['main_response'].url)
                    yield loader.load_item()

            return

        if not products and prices:
            product_id = hxs.select('//span[@class="eBprice"]/@id').re('pP(.*)')
            if product_id:
                price = prices.get(product_id[0]) or eBzpp[0]
            else:
                price = eBzpp[0]

            p = Product()
            loader = ProductLoader(response=price_response.meta['main_response'], item=p)
            loader.add_value('name', main_name)
            loader.add_value('price', price)
            loader.add_value('url', price_response.meta['main_response'].url)
            yield loader.load_item()

        for product in products:
            subprods = product.select('./@value').extract()[0].split(',')
            if len(subprods) == 1 and subprods[0] in prices and subprods[0] not in unpriced:
                p = Product()
                loader = ProductLoader(response=price_response.meta['main_response'], item=p)
                subname = product.select('./text()').extract()[0].strip()
                loader.add_value('name', main_name + ' ' + subname)
                loader.add_value('price', prices[subprods[0]])
                loader.add_value('url', price_response.meta['main_response'].url)
                yield loader.load_item()

            elif len(subprods) > 1:
                subprods = subprods[1:]
                for i, subprod in enumerate(subprods):
                    if subprod in prices and subprod not in unpriced:
                        p = Product()
                        loader = ProductLoader(response=price_response.meta['main_response'], item=p)
                        loader.add_value('url', price_response.meta['main_response'].url)
                        first_subname = product.select('./text()').extract()[0].strip()
                        subname = subprods[i - 1].strip()
                        loader.add_value('name', unquote(main_name + ' ' + first_subname + ' ' + subname))
                        loader.add_value('price', prices[subprod])
                        yield loader.load_item()

        alternate_prices = hxs.select('//a[@class="green2"]')
        for alt in alternate_prices:
            subprods = alt.select('./following-sibling::em//text()').extract()
            for subprod in subprods:
                prod_data = subprod.split(':')
                if len(prod_data) > 1:
                    loader = ProductLoader(selector=alt, item=Product())
                    loader.add_value('url', price_response.meta['main_response'].url)
                    loader.add_value('name', main_name)
                    loader.add_value('name', prod_data[0])
                    loader.add_value('price', prod_data[1])
                    if not loader.get_output_value('price'):
                        continue

                    yield loader.load_item()