__author__ = 'juraseg'

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

import logging


class TescoComSagemcomSpider(BaseSpider):
    name = 'tesco.com_sagemcom'
    allowed_domains = ['tesco.com']
    start_urls = (
        'http://direct.tesco.com/',
        )
    search_url = 'http://www.tesco.com/direct/search-results/results.page?catId=4294967294&searchquery='

    keywords = ['Sagemcom']

    products = [
        'http://www.tesco.com/direct/humax-fox-t2-freeview-hd-digital-tv-recorder/209-9461.prd?skuId=209-9461&pageLevel=sku&_requestid=1032662',
        'http://www.tesco.com/direct/humax-foxsat-500gb-freesat-dtr/212-3198.prd?skuId=212-3198&pageLevel=sku&_requestid=1034685',
        'http://www.tesco.com/direct/philips-ppx1230-pocket-projector-30-lumens/211-1532.prd?skuId=211-1532&pageLevel=&sc_cmp=ppc_g_ppx1230_p&gclid=CMv92szip7ACFcwNtAodAzh1XQ',
        'http://www.tesco.com/direct/philips-ppx1430-multi-media-pocket-projector-with-mp4-player/211-8666.prd?skuId=211-8666&pageLevel=&sc_cmp=ppc_g_ppx1430_p&gclid=CP_1sJjkp7ACFcwNtAodAzh1XQ',
        'http://www.tesco.com/direct/3m-mp160-pocket-lcos-projector-black/212-7816.prd',
        'http://www.tesco.com/direct/acer-c110-pico-projector/215-8176.prd?skuId=215-8176&pageLevel=&sc_cmp=ppc_g_acer%20c110_p&gclid=CLzQsIz2p7ACFcshtAodpGq7Wg',
        'http://www.tesco.com/direct/acer-c112-pico-projector/215-3897.prd?skuId=215-3897&pageLevel=&sc_cmp=ppc_g_c112_p&gclid=COCl5M32p7ACFUdItAod430cWA',
        'http://www.tesco.com/direct/acer-k10-pico-projector/208-0002.prd',
        'http://www.tesco.com/direct/philips-ppx2480-projector-black/215-3313.prd;jsessionid=16kvSTHsckg66E2bU79-kg',
        'http://www.tesco.com/direct/philips-ppx2055-projector/215-2648.prd;jsessionid=druv13MJfi3Q2DFUD17-Zw**.UKTULLF54V_slot3?skuId=215-2648&pageLevel=',
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

        name = hxs.select("//div[@class='primary-content']//div[@id='product-summary']/h1/text()").extract()

        if not name:
            name = hxs.select('//h1/text()').extract()
        if not name:
            logging.error("ERROR! NO NAME! %s" % url)
            return
        name = name[0]

        price = hxs.select("//div[@class='secondary-content']//ul[@class='pricing']/li[@class='current-price']/span/text()").extract()
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
        base_url = get_base_url(response)

        # parse pages
        pages = hxs.select("//div[@class='pagination-link']//a/@href").extract()
        for page in pages:
            request = Request(urljoin_rfc(base_url, page), callback=self.parse_search)
            yield request

        # parse products
        items = hxs.select("//li[contains(@class, 'product')]")
        for item in items:
            name = item.select("div[@class='product-details']/div[contains(@class, 'product-name')]/h3/a/text()").extract()
            if not name:
                continue
            name = name[0]

            url = item.select("div[@class='product-details']/div[contains(@class, 'product-name')]/h3/a/@href").extract()
            if not url:
                logging.error("ERROR! NO URL! URL: %s. NAME: %s" % (response.url, name))
                continue
            url = url[0]
            url = urljoin_rfc(base_url, url)

            price = item.select("div[@class='product-details']/div[contains(@class, 'price-spacing')]/p[@class='current-price']/span[@class='pounds']/text()").extract()
            if not price:
                logging.error("ERROR! NO PRICE! URL: %s. NAME: %s" % (response.url, name))
                continue
            price = price[0]

            price2 = item.select("div[@class='product-details']/div[contains(@class, 'price-spacing')]/p[@class='current-price']/span[@class='pence']/text()").extract()
            if price2:
                price += "." + price2[0]

            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', name)
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()
