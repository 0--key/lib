import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class ClivecoffeeComSpider(BaseSpider):
    name = 'clivecoffee.com'
    allowed_domains = ['clivecoffee.com']
    start_urls = ('http://www.clivecoffee.com/',)

    def parse(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # categories
        category_urls = hxs.select("//div[@id='nav']/ul/li/a/@href").extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        # subcategories
        subcategory_urls = hxs.select("//div[@id='side-nav']/ul/li//a/@href").extract()
        for url in subcategory_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        # products list
        products = hxs.select("//div[contains(@class, 'prodListItemWrapIn')]")
        if not products:
            print "ERROR!! NO PRODUCTS!! %s " % response.url
            logging.error("ERROR!! NO PRODUCTS!! %s " % response.url)
        for product_el in products:
            name = product_el.select(".//h2[@class='prodTitle']/a/text()").extract()
            if not name:
                print "ERROR!! NO NAME!! %s " % response.url
                logging.error("ERROR!! NO NAME!! %s " % response.url)
                continue
            name = name[0]

            url = product_el.select(".//h2[@class='prodTitle']/a/@href").extract()
            if not url:
                print "ERROR!! NO URL!! %s" % response.url
                logging.error("ERROR!! NO URL!! %s " % response.url)
                continue
            url = url[0]
            url = urljoin_rfc(URL_BASE, url)

            price = product_el.select(".//div[@class='prodPrice']//text()").extract()
            if not price:
                print "ERROR!! NO PRICE!! %s" % response.url
                logging.error("ERROR!! NO PRICE!! %s " % response.url)
                continue
            price = price[0]

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()