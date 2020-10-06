import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

import logging


class FireplaceworldCoUkSpider(BaseSpider):
    name = 'argos.co.uk'
    allowed_domains = ['argos.co.uk']
    start_urls = ('http://www.argos.co.uk/static/Home.htm',)

    start_products = (
        'http://www.argos.co.uk/webapp/wcs/stores/servlet/Search?storeId=10001&catalogId=1500002951&langId=-1&searchTerms=WINDSOR+OAK+AND+BLACK',
        'http://www.argos.co.uk/webapp/wcs/stores/servlet/Search?storeId=10001&catalogId=1500002951&langId=-1&searchTerms=IRAD',
    )

    def parse_products(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # check if individual product page or products list
        name = hxs.select("//div[@id='pdpProduct']/h1/text()").extract()
        if name:
            name = name[0]
            url = response.url
            price = hxs.select("//div[@id='pdpPricing']/span[@class='actualprice']/span/text()").extract()
            if not price:
                logging.error("ERROR!! NO PRICE!! %s " % url)
                return
            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()
            return
            #continue if not

        # all_products link
        all_products_url = hxs.select("//div[@class='paginglinks']//a[@class='allproducts']/@href").extract()
        if all_products_url:
            url = urljoin_rfc(URL_BASE, all_products_url[0])
            yield Request(url, callback=self.parse_products)
            return
            #continue if not found

        # pages
        page_urls = hxs.select("//div[@class='paginglinks']//a/@href").extract()
        for url in page_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url, callback=self.parse_products)

        # products list
        products = hxs.select("//div[@id='switchview']/ol/li/ul")
        if not products:
            logging.error("ERROR!! NO PRODUCTS!! %s " % response.url)
        for product_el in products:
            name = product_el.select('li[@class="producttitle"]/h4/a[1]/text()').extract()
            if not name:
                logging.error("ERROR!! NO NAME!! %s" % response.url)
                continue

            url = product_el.select('li[@class="producttitle"]/h4/a[1]/@href').extract()
            if not url:
                logging.error("ERROR!! NO URL!! %s %s" % (response.url, name))
                continue
            url = url[0]

            price = product_el.select('li[contains(@class, "pricing")]/ul/li[contains(@class, "price ")]/text()').extract()
            if not price:
                logging.error("ERROR!! NO PRICE!! %s %s" % (response.url, name))
                continue
            price = price[0]

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()

    def parse_subcategories(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # subcategories
        category_urls = hxs.select("//div[@id='listerlhs']//a/@href").extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url, callback=self.parse_products)

    def parse(self, response):
        URL_BASE = get_base_url(response)
        # search categories for 'fireplaces'
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//div[@id="dropdownmenus"]//a')
        for category_link in category_urls:
            # check if title or text contains 'fireplaces'
            link_title = category_link.select("@title").extract()
            link_text = category_link.select("text()").extract()
            m1, m2 = None, None
            if link_title:
                m1 = re.match("^.*?fireplaces.*?$", link_title[0], flags=re.IGNORECASE)
            if link_text:
                m2 = re.match("^.*?fireplaces.*?$", link_text[0], flags=re.IGNORECASE)
            if m1 or m2:
                url = category_link.select("@href").extract()[0]
                url = urljoin_rfc(URL_BASE, url)
                yield Request(url, callback=self.parse_subcategories)

        for product_link in self.start_products:
            yield Request(product_link, callback=self.parse_products)
