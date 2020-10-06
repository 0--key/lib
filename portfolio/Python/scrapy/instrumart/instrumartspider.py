import re
import json

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.utils import extract_price

class InstrumartSpider(BaseSpider):
    name = 'instrumart.com'
    allowed_domains = ['instrumart.com']
    start_urls = ('http://www.instrumart.com/categories',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        if response.url == self.start_urls[0]:
            cats = hxs.select('//div[@class="container_12 clearfix"]//a/@href').extract()
            for cat in cats:
                yield Request(urljoin_rfc(get_base_url(response), cat))

        pages = hxs.select('//div[@class="paging"]//a/@href').extract()
        for page in pages:
            yield Request(urljoin_rfc(get_base_url(response), page))

        for product in self.parse_products(hxs, response):
            yield product


    def parse_products(self, hxs, response):
        products = hxs.select('//div[@id="products"]//div[@class="price"]/../..')
        for product in products:
            url = urljoin_rfc(get_base_url(response), product.select('.//a/@href').extract()[0])
            p = ProductLoader(selector=product, item=Product())
            p.add_value('url', url)
            p.add_xpath('name', './td[2]//a/text()')
            if product.select('.//div[@class="starting-at"]'):
                product_id = url.split('/')[-2]
                yield Request('http://www.instrumart.com/products/configuratorjson/%s' % product_id,
                              callback=self.parse_options, meta={'loader': p})
            else:
                p.add_xpath('price', './/div[@class="our-price discounted"]/text()')
                p.add_xpath('price', './/div[@class="our-price"]/text()')
                yield p.load_item()

    def parse_options(self, response):
        loader = response.meta['loader']
        seen = []
        url = loader.get_output_value('url')
        main_name = loader.get_output_value('name')
        options_data = json.loads(response.body)
        base_price = extract_price(str(options_data['startingPrice']))
        if base_price:
            p = ProductLoader(response=response, item=Product())
            p.add_value('url', url)
            p.add_value('name', main_name)
            p.add_value('price', base_price)
            yield p.load_item()

        for option in options_data['options']:
            for value in option['values']:
                if value.get('cost') and not value['description'] in seen:
                    seen.append(value['description'])
                    p = ProductLoader(response=response, item=Product())
                    p.add_value('url', url)
                    p.add_value('name', main_name + ' ' + value['description'])
                    p.add_value('price', base_price + extract_price(str(value['cost'])))
                    yield p.load_item()
