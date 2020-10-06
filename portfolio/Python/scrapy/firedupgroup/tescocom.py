from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

import logging


class TescoComSpider(BaseSpider):
    name = 'tesco.com'
    allowed_domains = ['tesco.com']
    start_urls = (
    'http://www.tesco.com/direct/home-electrical/fires/cat3376574.cat',
    )

    def parse(self, response):
        URL_BASE = get_base_url(response)

        hxs = HtmlXPathSelector(response)

        pages_urls = hxs.select("//div[contains(@class, 'pagination')]/a/@href").extract()
        for url in pages_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        products_els = hxs.select("//li[contains(@class, 'product')]/div[@class='product-details']")
        for product_el in products_els:
            name = product_el.select("div[contains(@class, 'product-name')]/h3/a/text()").extract()
            if not name:
                logging.error('ERROR!! NO NAME!! %s' % response.url)
                continue
            name = " ".join(name)

            url = product_el.select("div[contains(@class, 'product-name')]/h3/a/@href").extract()
            if not url:
                logging.error('ERROR!! NO URL!! %s %s' % (response.url, name))
                continue
            url = url[0]
            url = urljoin_rfc(URL_BASE, url)

            price = product_el.select("div[contains(@class, 'price-spacing')]/p[@class='current-price']/span[@class='pounds']/text()").extract()
            price2 = product_el.select("div[contains(@class, 'price-spacing')]/p[@class='current-price']/span[@class='pence']/text()").extract()
            if not price:
                logging.error('ERROR!! NO PRICE!! %s %s' % (response.url, name))
                continue
            price = price[0]
            if price2:
                price += "." + price2[0]

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)

            loader.add_value('sku', '')

            yield loader.load_item()
