import re
from decimal import Decimal

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

import logging

class BigrocksupplyComSpider(BaseSpider):
    name = "bigrocksupply.com"
    allowed_domains = ["bigrocksupply.com"]
    start_urls = (
        'http://www.bigrocksupply.com/Roof-Drains.html',
        'http://www.bigrocksupply.com/Pipe-Penetrations.html',
        )

    download_delay = 3

    def parse(self, response):
        base_url = get_base_url(response)

        hxs = HtmlXPathSelector(response)

        pages = hxs.select(
            "//div[contains(@class, 'Pagination')]//a/@href"
        ).extract()
        for page in pages:
            yield Request(urljoin_rfc(base_url, page), callback=self.parse)

        items = hxs.select(
            "//table[@id='dlCategory']//div[@class='CategoryItem']/\
               div[@class='CategoryItemThumbnail']/a/@href"
        ).extract()
        for item in items:
            yield Request(
                urljoin_rfc(base_url, item),
                callback=self.parse_item
            )

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        name = hxs.select(
            "//h1[@class='ProductDetailsProductName']/text()"
        ).extract()
        if not name:
            logging.error("No product name! %s" % response.url)
            return
        name = name[0]

        url = response.url

        price = hxs.select(
            "//div[@class='ProductDetailsPricing']/\
               span[@class='ProductDetailsPriceArea']/\
               span[@id='lblPrice']/text()"
        ).re("\$([\d.]+)")
        if not price:
            logging.error("No product price! %s %s" % (name, response.url))
            return
        price = price[0]
        price = Decimal(price)

        options = hxs.select(
            "//div[@class='ProductDetailsVariations']/\
               select[@class='variantDropDown']/option"
        )
        found_products = False
        if options:
            # adding products variations from options
            for option in options:
                text = option.select("text()").extract()[0]
                m = re.search("(.*?)[\s]*/[\s]*add[\s]*\$([\d.]+)$", text)
                if m:
                    name_part = m.group(1)
                    if name_part == 'Please Select':
                        continue
                    item_name = name + " " + name_part
                    item_price = price + Decimal(m.group(2))
                    l = ProductLoader(item=Product(), response=response)
                    l.add_value('identifier', str(item_name))
                    l.add_value('name', item_name)
                    l.add_value('url', url)
                    l.add_value('price', item_price)
                    yield l.load_item()
                    found_products = True
                    continue
                m = re.search("(.*?)[\s]*/[\s]*\$([\d.]+)$", text)
                if m:
                    name_part = m.group(1)
                    if name_part == 'Please Select':
                        continue
                    item_name = name + " " + name_part
                    item_price = m.group(2)
                    l = ProductLoader(item=Product(), response=response)
                    l.add_value('identifier', str(item_name))
                    l.add_value('name', item_name)
                    l.add_value('url', url)
                    l.add_value('price', item_price)
                    yield l.load_item()
                    found_products = True
                    continue

                item_name = name + " " + text
                if text == 'Please Select':
                    continue
                l = ProductLoader(item=Product(), response=response)
                l.add_value('identifier', str(item_name))
                l.add_value('name', item_name)
                l.add_value('url', url)
                l.add_value('price', price)
                yield l.load_item()
                found_products = True

        if not found_products:
            # adding one product
            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', str(name))
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()
