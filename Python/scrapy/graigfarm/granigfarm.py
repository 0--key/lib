import re
import os
import csv
import hashlib
import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
from product_spiders.items import Product, ProductLoaderWithNameStrip\
                             as ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))


class GraigFarmSpider(BaseSpider):

    name = 'graigfarm.co.uk'
    allowed_domains = ['www.graigfarm.co.uk', 'graigfarm.co.uk']
    start_urls = ('http://www.graigfarm.co.uk/organic-produce-c1',
                  'http://www.graigfarm.co.uk/non-organic-produce-c7',)

    PRODUCT_URL = 'http://www.graigfarm.co.uk/ajax/get_product_options/%s'
    OPTION_URL = 'http://www.graigfarm.co.uk/ajax/get_product_options/%s?attributes[1]=%s&quantity=1'
    NO_OPTION_URL = 'http://www.graigfarm.co.uk/ajax/get_product_options/%s?quantity=1'

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # getting product links from product list
        prod_ids = hxs.select('//p[@class="product_options"]/a/@href').extract()
        prod_urls = [url for url in prod_ids[1::2]]
        prod_ids = [id.split('/')[2] for id in prod_ids[::2]]
        ids_urls = zip(prod_ids, prod_urls)
        #log.msg("ids - %s" % ids_urls)
        for prod_id, prod_url in ids_urls:
            url = urljoin_rfc(get_base_url(response),
                              self.PRODUCT_URL % prod_id)
            request = Request(url, callback=self.parse_product_options)
            request.meta['prod_id'] = prod_id
            request.meta['prod_url'] = prod_url
            yield request

        # pages
        next_page = hxs.select('//a[@class="next_page page_num"]/@href').extract()
        if next_page:
            url = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(url)

    def parse_product_options(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        prod_id = response.meta['prod_id']
        prod_url = response.meta['prod_url']

        vals_str = hxs.select('//p/text()').extract()[0]
        option_ids = re.findall('"value_id":"(\d+)', vals_str)
        if option_ids:
            for option_id in option_ids:
                url = urljoin_rfc(get_base_url(response),
                                  self.OPTION_URL % (prod_id, option_id))
                request = Request(url, callback=self.parse_product)
                #passing through prod_url
                request.meta['prod_url'] = response.meta['prod_url']
                yield request
        else:
            url = urljoin_rfc(get_base_url(response),
                              self.NO_OPTION_URL % (prod_id))
            request = Request(url, callback=self.parse_product)
            #passing through prod_url
            request.meta['prod_url'] = response.meta['prod_url']
            yield request
            

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        prod = hxs.extract()
        if prod:
            url = response.meta['prod_url']
            url = urljoin_rfc(self.start_urls[0], url)
            name = re.search('"title":"([^"]*)"+', prod).group()
            name = name.split(":")[1].strip('"').strip()
            if name:
                name_sufix = ''
                loader = ProductLoader(item=Product(), selector=hxs)
                loader.add_value('url', url)
                sku = re.search('"reference":"(?:[^\\"]+|\\.)*"', prod)#re.search('"reference":"(\d+-\d+\S\s+\w+)', prod)
                if not sku:
                    sku = re.search('"reference":"(\d+-\d+\S\w+)', prod)
                if sku:
                    sku = sku.group().split(':')[1].strip('",')    
                    loader.add_value('sku', sku)
                    loader.add_value('identifier', sku)
                    name_sufix = '-'.join(sku.split('-')[1:])
                if name_sufix:
                    loader.add_value('name', name+' ('+name_sufix+')')
                else:
                    loader.add_value('name', name)
                price = re.findall('"flat_price_inc":"(\d+.\d+)', prod)
                if price:
                    loader.add_value('price', price[0][:-1])
                yield loader.load_item()
