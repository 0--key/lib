import re
import json

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, TextResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy import log

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.utils import extract_price

class TestEquipmentDepotSpider(BaseSpider):
    name = 'testequipmentdepot.com'
    allowed_domains = ['testequipmentdepot.com']
    start_urls = ('http://www.testequipmentdepot.com/newcatalog.htm',)

    def parse(self, response):
        response = TextResponse(response.url, encoding='iso-8859-1', body=response.body, request=response.request)
        hxs = HtmlXPathSelector(response)
        cats = []
        if response.url == self.start_urls[0]:
            cats = hxs.select('//td/p/a/@href').extract()
            cats += hxs.select('//li//a[@class="noline2"]/@href').extract()

        price_list_cats = []
        price_list = False
        if not response.meta.get('price_list'):
            price_list_cats = hxs.select('//a[contains(text(), "Price List") and contains(@href, "pricelist")]/@href').extract()

        if price_list_cats:
            price_list = True

        cats += price_list_cats
        cats += hxs.select('//div[@align="center"]/table//font/img/../../@href').extract()
        cats += hxs.select('//div[@align="center"]/table//span/img/../../@href').extract()
        cats += hxs.select('//div[@align="center"]/table//a/img/../@href').extract()
        if not price_list:
            cats += hxs.select('//table//td[@class="catalog3"]//a/@href').extract()

        cats += hxs.select('//table//td[@class="graybg"]//span/../@href').extract()
        cats += hxs.select('//table//td[@class="graybg"]//span/../../@href').extract()
        cats += hxs.select('//table//td[@class="graybg"]//span/a/@href').extract()

        for cat in cats:
            if "action=buy_now" not in cat:
                url = urljoin_rfc(get_base_url(response), cat)
                if len(re.findall('\.htm', url)) > 1 or len(re.findall('\.asp', url)) > 1:
                    continue

                yield Request(url, encoding='iso-8859-1',
                              meta={'price_list': price_list or response.meta.get('price_list')})


        for product in self.parse_products(hxs, response):
            yield product

    def parse_products(self, hxs, response):
        print response.encoding
        model_pos = hxs.select('count(//td[starts-with(@class, "orderinfo")' +
                               ' and text()="Model"]/preceding-sibling::*) + 1').extract()
        description_pos = hxs.select('count(//td[starts-with(@class, "orderinfo")' +
                                     ' and text()="Description"]/preceding-sibling::*) + 1').extract()
        price_pos = hxs.select('count(//td[starts-with(@class, "orderinfo")' +
                                ' and text()="Price"]/preceding-sibling::*) + 1').extract()

        if model_pos and description_pos and price_pos:
            model_pos = model_pos[0].split('.')[0]
            description_pos = description_pos[0].split('.')[0]
            price_pos = price_pos[0].split('.')[0]

            products = hxs.select('//td[starts-with(@class, "orderinfo") and position()=%s \
                                   and not(text()="Model")]/..' % model_pos)
            for product in products:
                loader = ProductLoader(selector=product, item=Product())
                url = response.url
                model_url = product.select('.//td[starts-with(@class, "orderinfo") \
                                            and position()=%s]//a/@href' % model_pos).extract()
                if model_url:
                    url = urljoin_rfc(get_base_url(response), model_url[0])

                loader.add_value('url', url)
                loader.add_xpath('name', './/td[starts-with(@class, "orderinfo") and position()=%s]/text()' % description_pos)
                loader.add_xpath('price', './/td[starts-with(@class, "orderinfo") and position()=%s]//text()' % price_pos)
                if not loader.get_output_value('price') or not loader.get_output_value('name').strip():
                    continue

                yield loader.load_item()
