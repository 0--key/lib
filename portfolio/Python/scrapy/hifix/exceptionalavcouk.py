import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class ExceptionalAvCoUkSpider(BaseSpider):
    name = 'exceptional-av.co.uk'
    allowed_domains = ['exceptional-av.co.uk']
    start_urls = ('http://exceptional-av.co.uk',)

    def parse(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # categories
        category_urls = hxs.select('//div[@id="navbox"]/ul/li//a/@href').extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        # one product
        product = hxs.select("//td[@class='shopInformation']")
        if product:
            name = hxs.select("//span[@class='shopPageTitle']/text()[last()]").re(" > (.*)$")
            if not name:
                logging.error("ERROR!! NO NAME!! %s" % response.url)

            url = response.url

            price = product.select("form/span[1]//text()").extract()
            if not price:
                price = product.select("span[1]//text()").extract()
                if not price:
                    logging.error("ERROR!! NO PRICE!! %s" % response.url)

            if name and price:
                name = name[0]
                price = price[0]
                product = Product()
                loader = ProductLoader(item=product, response=response)
                loader.add_value('url', url)
                loader.add_value('name', name)
                loader.add_value('price', price)
                yield loader.load_item()

        # products list
        products = hxs.select("//td[@class='shopSummary']")
        for product_el in products:
            name = product_el.select("table[1]/tr[1]/td[1]/a/text()").extract()
            if not name:
                continue
            name = name[0]

            url = product_el.select("table[1]/tr[1]/td[1]/a/@href").extract()
            if not url:
                logging.error("ERROR!! NO URL!! %s %s" % (response.url, name))
                continue
            url = url[0]
            url = urljoin_rfc(URL_BASE, url)

            price = product_el.select("table/form/tr/td/span[1]/text()").extract()
            if not price:
                price = product_el.select("table/tr[last()]/td/span[1]/text()").extract()
                if not price:
                    logging.error("ERROR!! NO PRICE!! %s %s" % (response.url, name))
                    continue

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            yield loader.load_item()

        if not products and not product:
            logging.error("ERROR!! NO PRODUCTS!! %s " % response.url)