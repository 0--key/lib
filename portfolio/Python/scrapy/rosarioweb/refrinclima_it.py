from scrapy.spider import BaseSpider

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader
from product_spiders.utils import extract_price2uk
from decimal import Decimal

import logging

class RefrinclimaItSpider(BaseSpider):
    name = "refrinclima.it"
    allowed_domains = ["refrinclima.it"]
    start_urls = (
        'http://www.refrinclima.it/',
        )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        categories = hxs.select("//div[@class='main-menu']/div[@class='menu']/ul/li//a/@href").extract()
        for category in categories:
            yield Request(category, callback=self.parse)

        pages = hxs.select("//div[@class='pagination']/ul[@class='pagination']/li/a/@href").extract()
        for page in pages:
            yield Request(page, callback=self.parse)

        products = hxs.select("//ul[@id='product_list']/li")
        for product in products:
            url = product.select("div/h5/a/@href").extract()[0]
            yield Request(url, callback=self.parse_item)

            
    def parse_item(self, response):
        url = response.url

        hxs = HtmlXPathSelector(response)
        name = hxs.select("//div[@id='primary_block']/div[@id='pb-left-column']/h2/text()").extract()
        if not name:
            logging.error("NO NAME! %s" % url)
            return
        name = name[0]

        price = hxs.select("//p[@class='price']/span[@class='our_price_display']/span/text()").extract()
        if not price:
            logging.error("NO PRICE! %s" % url)
            return
        price = price[0]
        price = Decimal(extract_price2uk(price))

        eco_tax = hxs.select("//p[@class='price-ecotax']/span/text()").extract()
        if eco_tax:
            eco_tax[0] = eco_tax[0].encode('ascii', 'ignore')
            print "Found eco tax %s" % eco_tax[0]
            price -= Decimal(extract_price2uk(eco_tax[0]))
        
        l = ProductLoader(item=Product(), response=response)
        l.add_value('identifier', str(name))
        l.add_value('name', name)
        l.add_value('url', url)
        l.add_value('price', unicode(price))
        yield l.load_item()