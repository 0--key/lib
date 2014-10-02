import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode

import csv

from product_spiders.items import Product, ProductLoader


class SuperFiSpider(BaseSpider):
    name = 'superfi.co.uk'
    allowed_domains = ['www.superfi.co.uk', 'superfi.co.uk']
    start_urls = ('http://superfi.co.uk/',)

    def __init__(self, *args, **kwargs):
        super(SuperFiSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//ul[@class="topnav"]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pages
        next_page = hxs.select(u'//div[@class="paging2"]//a[contains(text(),">>")]/@href').extract()
        if next_page:
            url = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(url)

        # products
        products = hxs.select(u'//a[@class="compare_list_image"]/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)

    def parse_option_price(self, response):
        product_loader = ProductLoader(item=Product(), response=response)

        product_loader.add_value('name', response.meta['name'])
        product_loader.add_value('url', response.meta['url'])
        product_loader.add_xpath('price', u'//div[@class="webPriceLabel"]/text()',
                                     re=u'\xa3(.*)')
        yield product_loader.load_item()
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        base_name = hxs.select(u'//div[@class="ProductTopTitle"]/h1/text()').extract()
        multiple_options = hxs.select('//div[@class="variantdiv"]')
        if not multiple_options:
            product_loader = ProductLoader(item=Product(), response=response)
            product_loader.add_value('name', base_name)
            product_loader.add_value('url', response.url)
            product_loader.add_xpath('price', u'//div[@class="webPriceLabel"]/text()',
                                     re=u'\xa3(.*)')
            yield product_loader.load_item()
        else:
            color_options = multiple_options.select(u'.//select[contains(@id,"Color")]/option/@value').extract()
            size_options = multiple_options.select(u'.//select[contains(@id,"Size")]/option/@value').extract()
            
            if color_options:
                for color in color_options[1:]:
                    if size_options:
                        for size in size_options[1:]:
                            params = {'Colour': color, 'Size': size}
                            url = response.url + '?' + urlencode(params)
                            request = Request(url, callback=self.parse_option_price, dont_filter=True)
                            request.meta['name'] = base_name[0] + ' ' + size + ' ' + color
                            request.meta['url'] = response.url
                            yield request
                    else:
                        params = {'Colour': color}
                        url = response.url + '?' + urlencode(params)
                        request = Request(url, callback=self.parse_option_price, dont_filter=True)
                        request.meta['name'] = base_name[0] + ' ' + color
                        request.meta['url'] = response.url
                        yield request
            elif size_options:
                for size in size_options[1:]:
                    params = {'Size': size}
                    url = response.url + '?' + urlencode(params)
                    request = Request(url, callback=self.parse_option_price, dont_filter=True)
                    request.meta['name'] = base_name[0] + ' ' + size
                    request.meta['url'] = response.url
                    yield request
