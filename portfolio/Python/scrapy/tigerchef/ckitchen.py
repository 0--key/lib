import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.utils import extract_price

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class CKitchenSpider(BaseSpider):
    name = 'ckitchen.com'
    allowed_domains = ['ckitchen.com']
    start_urls = ('http://www.ckitchen.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        '''
        cats = hxs.select('//a[starts-with(@id, "a_op")]/@href').extract()
        '''
        cats = ['http://www.ckitchen.com/equipment/cecilware.html',
                'http://www.ckitchen.com/equipment/beverage-air.html']
        for cat in cats:
            yield Request(urljoin_rfc(get_base_url(response), cat))

        next_page = hxs.select('//a[@class="next"]/@href').extract()
        if next_page:
            yield Request(next_page[0])

        products = hxs.select('//div[@id="grid"]//p[@class="mi"]//a[position()=last()]/@href').extract()
        for product in products:
            yield Request(product, callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        main_name = hxs.select('//h1[@itemprop="name"]/text()').extract()[0].strip()
        main_price = hxs.select('//span[@itemprop="price"]/text()').extract()
        if not main_price:
            main_price = hxs.select('//input[@name="ppi"]/@value').extract()

        main_price = extract_price(main_price[0])

        loader = ProductLoader(response=response, item=Product())
        loader.add_value('name', main_name)
        loader.add_value('price', main_price)
        loader.add_value('url', response.url)
        loader.add_xpath('sku', '//span[@itemprop="identifier"]/text()')
        yield loader.load_item()


        def _add_options(option_sets, current_name, current_price):
            if not option_sets and current_price > main_price:
                loader = ProductLoader(response=response, item=Product())
                loader.add_value('url', response.url)
                loader.add_value('name', current_name)
                loader.add_value('price', current_price)
                yield loader.load_item()
            else:
                options = option_sets[0]
                option_sets = option_sets[1:]
                for option in options.select('./option/text()').extract():
                    r = re.search('(.*)\(Add(.*)\)', option)
                    name = current_name
                    price = current_price
                    if r:
                        name += ' ' + r.groups()[0].strip()
                        price += extract_price(r.groups()[1])
                    else:
                        name += ' ' + option

                    for product in _add_options(option_sets, name, price):
                        yield product

        option_sets = hxs.select('//div[@class="inn"]/select')
        if option_sets:
            for product in _add_options(option_sets, main_name, main_price):
                yield product

