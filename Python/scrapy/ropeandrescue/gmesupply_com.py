import re
import logging

from decimal import Decimal
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

def multiply(lst):
    if not lst:
        return [('', 0)]

    while len(lst) > 1:
        result = []
        for name0, price0 in lst[0]:
            for name1, price1 in lst[1]:
                result.append((name0 + ' ' + name1, float(price0) + float(price1)))
        lst = [result] + lst[2:]
    return lst[0]

class GmeSupplyComSpider(BaseSpider):
    name = 'gmesupply.com'
    allowed_domains = ['gmesupply.com']
    start_urls = ('http://www.gmesupply.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//nav[@id="main-nav"]/ul/li/a/@href').extract():
            yield Request(url, callback=self.parse_cats)

    def parse_cats(self, response):
        hxs = HtmlXPathSelector(response)

        cats = hxs.select(u'//div[@class="boxcenter" or @class="boxleft"]/@onclick').extract()
        if cats:
            for url in cats:
                url = url.split("'")[1]
                yield Request(url, callback=self.parse_product_list)
        for x in self.parse_product_list(response):
            yield x

    def parse_product_list(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[contains(@class,"product-tile-link")]/a/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)

        next_url = hxs.select(u'//div[@class="pages"]//li/a[@class="next"]/@href').extract()
        if next_url:
            yield Request(next_url[0], callback=self.parse_product_list)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        opt_groups = []
        def fix_options(o):
            try:
                return (o[0], o[1].replace(',', ''))
            except:
                return (o[0], '0')

        for option in hxs.select(u'//div[@class="input-box"]//select'):
            opt_list = option.select(u'./option[position() != 1]/text()').extract()
            opt_list = [o.replace('+$', '$').split('$') for o in opt_list]
            opt_groups.append([fix_options(o) for o in opt_list])

        for opt_name, opt_price in multiply(opt_groups):
            product_loader = ProductLoader(item=Product(), selector=hxs)
            product_loader.add_value('url', response.url)
            product_loader.add_xpath('name', u'//h2[@class="title"]/text()')
            product_loader.add_xpath('price', u'//span[contains(@class,"sale-price")]/text()')
            product_loader.add_xpath('sku', u'substring-after(//span[contains(@class,"meta-sku")]/text(),":")')
            product_loader.add_xpath('category', u'//ul[@class="breadcrumb"]/li[2]/a/@title')
            product_loader.add_xpath('image_url', u'//div[@class="teaser-large"]/img/@src')
            product_loader.add_xpath('brand', u'substring-after(//div[@class="product-meta"]/span[contains(text(),"Manufacturer:")]/text(),":")')
            product_loader.add_value('shipping_cost', '')

            product = product_loader.load_item()
            product['name'] = (product['name'] + ' ' + opt_name).strip()
            product['price'] = product['price'] + Decimal(opt_price)
            yield product
