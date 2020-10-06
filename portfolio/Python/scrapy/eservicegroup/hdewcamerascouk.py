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

class HdewcamerasCoUkSpider(BaseSpider):
    name = 'hdewcameras.co.uk'
    allowed_domains = (
        'hdewcameras.co.uk',
    )
    start_urls = (
        #'http://www.hdewcameras.co.uk/index.asp?function=CART&mode=CURRENCY&code=EUR&catid=&productid=',
        'http://www.hdewcameras.co.uk/index.asp?function=CART&mode=CURRENCY&code=GBP&catid=&productid=',
    )

    def __init__(self, *a, **kw):
        super(HdewcamerasCoUkSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        if spider.name == self.name:
            shutil.copy('data/%s_products.csv' % spider.crawl_id, os.path.join(HERE, 'hdewcamerascoukspider.csv'))
            log.msg("CSV is copied")

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        categories = hxs.select(
                "//div[@class='menu']/div[@class='stuff']/div[@class!='MultiCurrency']//a/@href"
                ).extract()
        for url in categories:
            yield Request(
                    url=self._urljoin(response, url)
                    )

        if len(hxs.select("//div[@class='product_cont']")) % 2 == 0:
            sub_categories = hxs.select(
                    "//div[@class='product_cont'][2]//a/@href"
                    ).extract()
            for url in sub_categories:
                yield Request(
                        url=self._urljoin(response, url)
                        )

        pages = hxs.select(
            "//center/font[@size='2']//a/@href"
            ).extract()
        for url in pages:
            yield Request(
                    url=self._urljoin(response, url)
                    )

        products = hxs.select("//div[@class='product_cont']/div[@class='products']/div[@class='row']")
        for product in products:
            name = product.select( "div[@class='description']/span[@class='title_link']/a/text()").extract()
            if not name:
                logging.error("Name not found!")
                continue
            name = name[0]

            url = product.select(
                    "div[@class='description']/span[@class='title_link']/a/@href"
                    ).extract()
            if not url:
                logging.error("Url not found!")
                continue
            url = self._urljoin(response, url[0])

            price = product.select("div[@class='price']/text()").extract()
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


