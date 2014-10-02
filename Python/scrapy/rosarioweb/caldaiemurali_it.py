from scrapy.spider import BaseSpider

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader
from decimal import Decimal

import logging

class CaldaiemuraliItSpider(BaseSpider):
    name = "caldaiemurali.it"
    allowed_domains = ["caldaiemurali.it"]
    start_urls = (
        'http://www.caldaiemurali.it/',
        )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        categories = hxs.select("//ul[@id='nav']//a/@href").extract()
        for category in categories:
            yield Request(category, callback=self.parse)

        pages = hxs.select("//div[@class='pages']/ol/li/a/@href").extract()
        for page in pages:
            yield Request(page, callback=self.parse)

        items = hxs.select("//div[@class='product-list-block']//a[@class='product-image']/@href").extract()
        for item in items:
            yield Request(item, callback=self.parse_item)

    def parse_item(self, response):
        url = response.url

        hxs = HtmlXPathSelector(response)
        name = hxs.select("//div[@class='product-shop']/div[@class='product-name']/h2/text()").extract()
        if not name:
            logging.error("NO NAME! %s" % url)
            return
        name = name[0]

        # adding product
        price = hxs.select("//div[@class='product-shop']/div[@class='price-box']//span[@class='price']/text()").extract()
        if not price:
            logging.error("NO PRICE! %s" % url)
            return
        price = price[0].replace(".", "").replace(",", ".")
#        price_delivery = hxs.select("//div[@class='product-shop']//table[@id='product-attribute-specs-table']/tr/td[(preceding::th[text()='Spese Spedizione'])]/text()").extract()
#        if not price_delivery:
#            logging.error("NO PRICE DELIVERY! %s" % url)
#            return
#        price_delivery = price_delivery[0]
#        price = Decimal(price) + Decimal(price_delivery)

        l = ProductLoader(item=Product(), response=response)
        l.add_value('identifier', str(name))
        l.add_value('name', name)
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()
