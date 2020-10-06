import re
import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class WholelatteloveComSpider(BaseSpider):
    name = 'wholelattelove.com'
    allowed_domains = ['wholelattelove.com']
    start_urls = ('http://www.wholelattelove.com/',)

    def parse(self, response):
        URL_BASE = get_base_url(response).replace('%20/', '')
        hxs = HtmlXPathSelector(response)

        # categories
        category_urls = hxs.select("//div[@id='navigation']//a/@href").extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url.replace('%20/', ''))

        # pagesproductlistsortfloatleft
        pages_urls = hxs.select("//div[@id='productlistsortfloatleft']//a/@href").extract()
        for url in pages_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url.replace('%20/', ''))

        # products list
        products = hxs.select("//div[starts-with(@class, 'grid-product')]")
        if not products:
            print "ERROR!! NO PRODUCTS!! %s " % response.url
            logging.error("ERROR!! NO PRODUCTS!! %s" % response.url)
        for product_el in products:
            name = product_el.select(".//div[@class='title']/a//text()").extract()
            if not name:
                continue
            name = name[0].strip()

            url = product_el.select(".//div[@class='title']/a/@href").extract()
            if not url:
                print "ERROR!! NO URL!! %s" % response.url
                continue
            url = url[0]
            url = urljoin_rfc(URL_BASE, url.replace('%20/', ''))

            price = product_el.select(".//div[@class='price ']/text()").extract()
            if not price:
                price = product_el.select(".//div[@class='price sale']/text()").extract()[1:]
            if not price:
                print "ERROR!! NO PRICE!! %s" % response.url
                continue
            price = price[0]
            m = re.search("(.*?)-(.*?)$", price)
            if m:
                price = m.group(1)

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url.replace('%20/', ''))
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()
