__author__ = 'juraseg'

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader

import logging

class AsdaComSpider(BaseSpider):
    name = 'asda.com'
    allowed_domains = ['asda.com']
    start_urls = (
        'http://direct.asda.com/',
        )
    search_url = 'http://direct.asda.com/on/demandware.store/Sites-ASDA-Site/default/Search-Show?q='

    products = [
        'http://direct.asda.com/Sagemcom-RTI90-320-Freeview-HD-Recorder/000513203,default,pd.html',
        ]

    keywords = ['Sagemcom']

    def parse(self, response):
        for keyword in self.keywords:
            url = self.search_url + keyword
            request = Request(url, callback=self.parse_search)
            yield request

        for url in self.products:
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        url = response.url

        name = hxs.select("//div[@id='productDetail']/form/fieldset/h2/text()").extract()
        if not name:
            logging.error("ERROR! NO NAME! %s" % url)
            return
        name = name[0]

        price = hxs.select("//div[@id='productDetail']/form/fieldset/div[@class='price']/span[@class='productPrice']/\
                              span[@class='pounds']/text()").extract()
        if not price:
            price = hxs.select("//div[@id='productDetail']/form/fieldset/div[@class='price']/span[@class='productPrice']/\
                              span[@class='newPrice']/text()").extract()
            if not price:
                logging.error("ERROR! NO PRICE! %s %s" % (url, name))
                return
        price = "".join(price)

        l = ProductLoader(item=Product(), response=response)
        l.add_value('identifier', name)
        l.add_value('name', name)
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()

    def parse_search(self, response):
        hxs = HtmlXPathSelector(response)

        # parse pages
        pages = hxs.select("//div[@class='searchBarPaging']/ul/li/a/@href").extract()
        for page in pages:
            request = Request(page, callback=self.parse_search)
            yield request

        # parse products
        items = hxs.select("//ul[@class='productListing clearfix']/li/div/div/form")
        for item in items:
            name = item.select("div[@class='listItemInnerMost']/div[@class='prodMiniTop']/h4/a/span/text()").extract()
            if not name:
                continue
            name = name[0]

            url = item.select("div[@class='listItemInnerMost']/div[@class='prodMiniTop']/h4/a/@href").extract()
            if not url:
                logging.error("ERROR! NO URL! URL: %s. NAME: %s" % (response.url, name))
                continue
            url = url[0]
            price = item.select("div[@class='listItemInnerMost']/div[@class='prodMiniBottom']/\
                                 span[@class='productPrice']/span[@class='pounds']/text()").extract()
            if not price:
                price = item.select("div[@class='listItemInnerMost']/div[@class='prodMiniBottom']/\
                                 span[@class='productPrice']/span[@class='newPrice']/text()").extract()
                if not price:
                    logging.error("ERROR! NO PRICE! URL: %s. NAME: %s" % (response.url, name))
                    continue
            price = price[-1]

            unique = item.select("div[@class='hidden']/input[@name='masterproduct_pid']/@value").extract()
            if not unique:
                logging.error("ERROR! NO UNIQUE! URL: %s. NAME: %s" % (response.url, name))
                continue
            unique = unique[0]

            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', "%s %s" % (name, unique))
            l.add_value('name', "%s %s" % (name, unique))
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()
