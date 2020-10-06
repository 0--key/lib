import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc


from scrapy.http import FormRequest
from productloader import load_product
import re
class CartridgeSave(BaseSpider):
    name = 'cartridgesave.co.uk'
    allowed_domains = ['cartridgesave.co.uk', 'www.cartridgesave.co.uk']
    start_urls = ('http://www.cartridgesave.co.uk',)

    def __init__(self, *args, **kwargs):
        super(CartridgeSave, self).__init__(*args, **kwargs)
        self.URL_BASE = 'http://www.cartridgesave.co.uk'
        self.product_name_re = re.compile('.*/(.*?)\.html')

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        res = {}
        try:
            # name = hxs.select('//div[@id="specification"]/ul/li[position()=1]').re('.* \((.*)\)')[0]
            url = response.url
            name = self.product_name_re.search(url).groups()[0]
            price = hxs.select('.//span[@class="ex_vat_price"]/text()').re('\xa3(.*)')[0]
            res['url'] = url
            res['description'] = name
            res['price'] = price
            res['sku'] = res['description']
            yield load_product(res, response)
        except IndexError:
            return


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        #categories
        hxs = HtmlXPathSelector(response)
        # printer brands
        printers_brands = hxs.select('//div[@id="manufacturers"]//li/a/@href').extract()
        for url in printers_brands:
            url = urljoin_rfc(self.URL_BASE, url)
            yield Request(url)
        # printer list
        printers_list = hxs.select('//ul[@class="printer_list"]//li/a/@href').extract()
        for url in printers_list:
            url = urljoin_rfc(self.URL_BASE, url)
            yield Request(url)


        # next page
        # next_page =
        # if next_page:
        #     url = urljoin_rfc(URL_BASE, next_page[0])
         #    yield Request(url)

        # products
        products = hxs.select('//div[@class="group_products"]//li/a[not(@class="lowest_price info")]/@href').extract()
        for product in products:
            product = urljoin_rfc(self.URL_BASE, product)
            yield Request(product, callback=self.parse_product)
