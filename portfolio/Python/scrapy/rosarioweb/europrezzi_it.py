# -*- coding: utf-8 -*-
from scrapy.spider import BaseSpider

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader
from decimal import Decimal

import logging

class EuroprezziItSpider(BaseSpider):
    name = "europrezzi.it"
    allowed_domains = ["europrezzi.it"]
    start_urls = (
        #'http://www.europrezzi.it/',
        'http://www.europrezzi.it/elettrodomestici/grandi-elettrodomestici?cat=20',
        'http://www.europrezzi.it/elettrodomestici/grandi-elettrodomestici?cat=38',
        'http://www.europrezzi.it/elettrodomestici/grandi-elettrodomestici?cat=41',
        'http://www.europrezzi.it/elettrodomestici/grandi-elettrodomestici?cat=42',
        'http://www.europrezzi.it/casa-ufficio-clima/clima?cat=130',
        'http://www.europrezzi.it/casa-ufficio-clima/clima?cat=146',
        'http://www.europrezzi.it/casa-ufficio-clima/clima?cat=133',
        'http://www.europrezzi.it/casa-ufficio-clima/casa?cat=263',
        'http://www.europrezzi.it/casa-ufficio-clima/casa?cat=335',
        )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        #categories = hxs.select("//div[@id='box_left_ctl02_livello_box']//table[@class='tabellaMenu']/tr/td[2]/a/@href").extract()
        #for category in categories:
            #yield Request(category, callback=self.parse)

        pages = hxs.select("//table[@class='pager']/tr/td[@class='pages']/ol/li/a/@href").extract()
        for page in pages:
            yield Request(page, callback=self.parse)

        items = hxs.select("//div[@class='listing-item ']/div[@class='product-image']/a/@href |\
                            //div[@class='listing-item last']/div[@class='product-image']/a/@href").extract()
        for item in items:
            yield Request(item, callback=self.parse_item)

    def parse_item(self, response):
        url = response.url

        hxs = HtmlXPathSelector(response)
        name = hxs.select("//h1[@class='product-name']/text()").extract()
        if not name:
            logging.error("NO NAME! %s" % url)
            return
        name = name[0]
                 
        # adding product
        price = hxs.select("//div[@class='price-box']//span[@class='price']/text()").re(u'€ (.*)')
        if not price:
            logging.error("NO PRICE! %s" % url)
            return
        price = price[0].replace(".", "").replace(",", ".")

        price_delivery = hxs.select("//div[@class='product-shop']/\
            text()[(preceding::div[@class='price-box']) and (following::div[@class='add-to-holder'])]"
        ).re(u'€\xa0([\d,.]*)')
        if not price_delivery:
            logging.error("NO PRICE DELIVERY! %s" % url)
            return
        price_delivery = price_delivery[0].replace(".", "").replace(",", ".")
        price = Decimal(price) + Decimal(price_delivery)

        l = ProductLoader(item=Product(), response=response)
        l.add_value('identifier', name.encode("ascii", "ignore"))
        l.add_value('name', name)
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()
