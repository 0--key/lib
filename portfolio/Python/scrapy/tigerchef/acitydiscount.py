import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.utils import extract_price

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader


class AcityDiscountSpider(BaseSpider):
    name = 'acitydiscount.com'
    user_agent = 'Googlebot/2.1 (+http://www.google.com/bot.html)'
    allowed_domains = ['acitydiscount.com']

    def start_requests(self):
        yield Request('http://www.acitydiscount.com')

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        '''
        cats = hxs.select('//li[@class="g-item"]/ul//a/@href').extract()
        cats += hxs.select('//h3[@class="titlegroups"]/a/@href').extract()
        '''
        cats = ['http://www.acitydiscount.com/Wisco.1.97.3.1.htm',
                'http://www.acitydiscount.com/Thunder-Group-Inc.1.2348.3.1.htm',
                'http://www.acitydiscount.com/Libbey.1.406.3.1.htm',
                'http://www.acitydiscount.com/Victory.1.57.3.1.htm',
                'http://www.acitydiscount.com/Vollrath.1.266.3.1.htm',
                'http://www.acitydiscount.com/F-Dick.1.1528.3.1.htm',
                'http://www.acitydiscount.com/Cecilware.1.48.3.1.htm',
                'http://www.acitydiscount.com/Turbo-Air-Radiance.1.2372.3.1.htm',
                'http://www.acitydiscount.com/G-E-T-.1.1137.3.1.htm',
                'http://www.acitydiscount.com/Beverage-Air.1.13.3.1.htm',
                'http://www.acitydiscount.com/Turbo-Air.1.915.3.1.htm',
                'http://www.acitydiscount.com/Amana.1.128.3.1.htm']

        for cat in cats:
            yield Request(cat)

        next_page = hxs.select('//a[@class="pagelinks" and contains(text(), "Next")]/@href').re('\d+')
        if next_page:
            manuf = re.search("manuf=(\d+)", response.body).groups()[0]
            pagination_url = 'http://www.acitydiscount.com/restaurant_equipment/index.cfm' + \
                             '?_faction=1&manuf=%s&startrow=%s' % (manuf, next_page[0])

            yield Request(pagination_url)

        products = hxs.select('//input[contains(@src, "btn_add2cart.gif")]/../..//a[position()=1]/@href').extract()
        for product in products:
            yield Request(product, self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        main_name = hxs.select('//h1[@class="titleadditional"]/text()').extract()[0].strip()
        price = hxs.select('//span[@id="current_price"]/span/text()').extract()[0]
        loader = ProductLoader(response=response, item=Product())
        loader.add_value('url', response.url)
        loader.add_value('name', main_name)
        loader.add_value('price', price)
        loader.add_xpath('sku', '//div[@id="product_description"]//td[contains(text(), "Model:")]' +
                                '/following-sibling::td[not(contains(text(), "*"))]/text()')
        yield loader.load_item()

        '''
        def _add_options(option_sets, current_name):
            if not option_sets:
                loader = ProductLoader(response=response, item=Product())
                loader.add_value('url', response.url)
                loader.add_value('name', current_name)
                loader.add_value('price', price)
                yield loader.load_item()
            else:
                options = option_sets[0]
                option_sets = option_sets[1:]
                for option in options.select('./option/text()').extract():
                    name = current_name.strip() + ' ' + option.strip()

                    for product in _add_options(option_sets, name):
                        yield product


        option_sets = hxs.select('//div[@id="product_price"]//select')
        if option_sets:
            for product in _add_options(option_sets, main_name):
                yield product
        '''
