import logging
import shutil
import os

from scrapy import signals
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.xlib.pydispatch import dispatcher
from scrapy import log

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class BignormanComSpider(BaseSpider):
    name = 'bignorman.com'
    allowed_domains = (
        'bignorman.com',
    )
    start_urls = (
        'http://www.bignorman.com',
    )

    def __init__(self, *a, **kw):
        super(BignormanComSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        if spider.name == self.name:
            shutil.copy('data/%s_products.csv' % spider.crawl_id, os.path.join(HERE, 'bignormancomspider.csv'))
            log.msg("CSV is copied")

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        categories = hxs.select("//ul[@id='nav-main']/li//a/@href").extract()
        for url in categories:
            yield Request(
                    url=self._urljoin(response, url), 
                    callback=self.parseProducts
                    )

    def parseProducts(self, response):
        hxs = HtmlXPathSelector(response)

        accessories = hxs.select(
            "//div[@id='sidebar']/ul/li/a/@href"
            ).re(".*Accessories.*")
        for url in accessories:
            yield Request(
                    url=self._urljoin(response, url), 
                    callback=self.parseProducts
                    )

        products = hxs.select("//ul[@class='list-products']/li/div/p")
        for product in products:
            name = product.select(
                    "a[@class='productnamecolour']/text()"
                    ).extract()
            if not name:
                logging.error("Name not found!")
                continue
            name = name[0]

            url = product.select(
                    "a[@class='productnamecolour']/@href"
                    ).extract()
            if not url:
                logging.error("Url not found!")
                continue
            url = self._urljoin(response, url[0])

            price = product.select(
                    "span/a[@class='productnamecolourred']/strong/text()"
                    ).extract()
            if not price:
                logging.error("Price not found!")
                continue
            price = price[0]

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            yield loader.load_item()


    def _urljoin(self, response, url):
        return urljoin_rfc(get_base_url(response), url)

