# -*- coding: utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.response import get_base_url
from scrapy.http import Request

import urlparse

from product_spiders.items import ProductLoader, Product

__author__ = 'Theophile R. <rotoudjimaye.theo@gmail.com>'

class EventstadMusikkSpider(BaseSpider):
    name = "evenstadmusikk.no"
    allowed_domains = ["evenstadmusikk.no"]
    start_urls = ("http://evenstadmusikk.no/index.php", )

    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        self.navig_url_set = set()

        cat_urls = hxs.select('//div[@id="navColumnOne"]//a[@class="category-top"]/@href').extract()
        for cat_url in cat_urls:
            subcat_url = urlparse.urljoin(base_url, cat_url)
            self.navig_url_set.add(subcat_url)
            yield Request(subcat_url, callback=self.browse_and_parse)

    def browse_and_parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        for subcat_href in hxs.select('//div[@id="navColumnOne"]//a/@href').extract():
            subsubcat_url = urlparse.urljoin(base_url, subcat_href)
            if subsubcat_url not in self.navig_url_set:
                self.navig_url_set.add(subsubcat_url)
                yield Request(subsubcat_url, callback=self.browse_and_parse)

        next_page = hxs.select("//div[@id='productListing']//div[@id='productsListingListingTopLinks']//a[contains(., 'Neste')]/@href")
        if next_page:
            yield Request(next_page[0].extract(), callback=self.browse_and_parse)

        # parse product listing in this page, if any
        for tr in hxs.select('//div[@id="productListing"]//tr[@class="productListing-even" or @class="productListing-odd"]'):
            product_loader = ProductLoader(item=Product(), response=response)

            product_loader.add_value('url', tr.select(".//td[2]//a/@href").extract()[0])
            product_loader.add_value('name', tr.select(".//td[2]//a/text()").extract()[0])
            product_loader.add_value('price', tr.select(".//td[3]/text()").extract()[0].split("-")[0].split(" ")[1].replace('.', '').replace(',', '.'))

            yield product_loader.load_item()

        # edge case: product listing page with a single product
        product_price = hxs.select('//h2[@id="productPrices"]/text()').extract()
        if product_price:
            # this product listing page contains a single product
            product_loader = ProductLoader(item=Product(), response=response)

            product_loader.add_xpath('name', '//h1[@id="productName"]/text()')
            product_loader.add_value('url', response.url)
            product_loader.add_value('price', product_price[0].split("-")[0].split(" ")[1].replace('.', '').replace(',', '.'))

            yield product_loader.load_item()