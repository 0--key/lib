import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy import log

import csv

from product_spiders.items import Product, ProductLoader


class HiFixSpider(BaseSpider):
    name = 'hifix.co.uk'
    allowed_domains = ['www.hifix.co.uk']
    start_urls = ('http://www.hifix.co.uk/sitemap.lasso',)

    def __init__(self, *args, **kwargs):
        super(HiFixSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        products = hxs.select(u'//a/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product, cookies={}, meta={'dont_merge_cookies': True})

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        loaded = False
        multiple_prices = hxs.select(u'//select[@id="item"]/option/text()').extract()
        if not multiple_prices:
            names = hxs.select(u'//td/h1/text()').extract()

            prices = hxs.select(u'//span[@class="largeheadblackcentred"]/text()').extract()
            if len(names) > 1:
                names = names[1:]
                prices = prices[1:]

            for i, name in enumerate(names):
                if i >= len(prices):
                    break

                name = '-'.join(name.split('-')[:-1])
                price = prices[i]
                product_loader = ProductLoader(item=Product(), response=response)

                product_loader.add_value('name', name.strip())
                product_loader.add_value('url', response.url)
                product_loader.add_value('price', price)

                loaded = True
                yield product_loader.load_item()
        else:
            for name_and_price in multiple_prices:
                product_loader = ProductLoader(item=Product(), selector=name_and_price)
                name, price = re.match('(.*)-.*\xa3(.*)', name_and_price).groups()
  #              if not name or not price:
   #                 continue
                product_loader.add_value('name', name.strip())
                product_loader.add_value('url', response.url)
                product_loader.add_value('price', price)

                yield product_loader.load_item()
                loaded = True

        retries = response.meta.get('retries', 0)
        if not loaded and retries < 3:
            log.msg('Retrying %s' % response.url, level=log.WARNING)
            yield Request(response.url, meta={'retries': retries + 1},
                          dont_filter=True, callback=self.parse_product)