__author__ = 'juraseg'

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader

import logging


class ComeCoUkSpider(BaseSpider):
    name = 'comet.co.uk'
    allowed_domains = ['comet.co.uk']
    start_urls = (
        'http://www.comet.co.uk/',
        )
    search_url = 'http://www.comet.co.uk/webapp/wcs/stores/servlet/SearchResultsDisplayView?storeId=10151&catalogId=10002&langId=-1&searchTerm='

    keywords = ['Sagemcom', 'Sagem']

    products = [
        'http://www.comet.co.uk/p/Freeview-freesat-Recorders/buy-HUMAX-HDR-FOX-T2-Freeview-freesat-Recorder/680052',
        'http://www.comet.co.uk/p/Freeview-freesat-Recorders/buy-HUMAX-HDR-FOX-T2/1TB-Freeview-freesat-Recorder/735736',
        'http://www.comet.co.uk/p/Freeview-freesat-Recorders/buy-HUMAX-FOXSAT-HDR500-Freeview-freesat-Recorder/712930',
        'http://www.comet.co.uk/p/Freeview-freesat-Recorders/buy-PANASONIC-DMR-HW100EBK-Freeview-freesat-Recorder/767913',
        'http://www.comet.co.uk/p/Freeview-freesat-Recorders/buy-SAMSUNG-SMT-S7800-Freeview-freesat-Recorder/701467',
        'http://www.comet.co.uk/p/Freeview-freesat-Recorders/buy-SAGEMCOM-RTI90-320-Freeview-freesat-Recorder/621994',
        'http://www.comet.co.uk/p/Freeview-freesat-Recorders/buy-HUMAX-PVR9300T/500-Freeview-freesat-Recorder/787388',
        'http://www.comet.co.uk/p/Freeview-freesat-Recorders/buy-SONY-SVRHDT500B.CEK-Freeview-freesat-Recorder/700665',
        'http://www.comet.co.uk/p/Freeview-freesat-Recorders/buy-SAGEMCOM-RTI95-320-Freeview-freesat-Recorder/664121',
        'http://www.comet.co.uk/p/Freeview-freesat-Recorders/buy-PHILIPS-HDTP8530-Freeview-freesat-Recorder/600339',
        ]

    def start_requests(self):
        for keyword in self.keywords:
            url = self.search_url + keyword
            request = Request(url, callback=self.parse_search)
            yield request

        for url in self.products:
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        url = response.url

        name = hxs.select("//div[@id='product-content']//div[@id='product-header']/h1//text()").extract()
        if not name:
            logging.error("ERROR! NO NAME! %s" % url)
            return
        name = " ".join(name)

        price = hxs.select("//div[@id='product-content']//div[@id='productPrice']//p[@id='product-price']/text()").extract()
        if not price:
            logging.error("ERROR! NO PRICE! %s %s" % (url, name))
            return
        price = price[0]

        l = ProductLoader(item=Product(), response=response)
        l.add_value('identifier', name)
        l.add_value('name', name)
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()

    def parse_search(self, response):
        hxs = HtmlXPathSelector(response)

        # parse pages
        pages = hxs.select("//ul[@id='pagination']/li/a/@href").extract()
        for page in pages:
            request = Request(page, callback=self.parse_search)
            yield request

        # parse products
        items = hxs.select("//div[@class='column_one grid_list']/div")
        for item in items:
            name = item.select("div/div[@class='info']/div/h2/a/text()").extract()
            if not name:
                continue
            name = name[0]

            url = item.select("div/div[@class='info']/div/h2/a/@href").extract()
            if not url:
                logging.error("ERROR! NO URL! URL: %s. NAME: %s" % (response.url, name))
                continue
            url = url[0]
            price = item.select("div/div[@class='pricebox']/p[@id='product-price']/text()").extract()
            if not price:
                logging.error("ERROR! NO PRICE! URL: %s. NAME: %s" % (response.url, name))
                continue
            price = price[0]

            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', name)
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()
