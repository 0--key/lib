import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class CameraWorldSpider(BaseSpider):
    name = 'cameraworld.co.uk'
    allowed_domains = ['www.cameraworld.co.uk', 'cameraworld.co.uk']
    start_urls = ('http://www.cameraworld.co.uk/',)

    def __init__(self, *args, **kwargs):
        super(CameraWorldSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//div[@id="lmenu"]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pagination
        next_page = hxs.select(u'//a[child::b[contains(text(),"Next")]]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        # products
        for product in self.parse_product(response):
            yield product

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)
        products = hxs.select(u'//tr[@align="center" and child::td[child::a[@target="_top"]]]')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//a[@target="_top" and child::span]/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)
            product_loader.add_xpath('name', u'.//a[@target="_top"]/span/text()')
            product_loader.add_xpath('price', u'.//span[contains(@class,"price")]/text()',
                                             re=u'\xa3([\d\.,]+)')
            yield product_loader.load_item()