__author__ = 'juraseg'

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

import logging


class DixonsCoUkSpider(BaseSpider):
    name = 'dixons.co.uk'
    allowed_domains = ['dixons.co.uk']
    start_urls = (
        'http://www.dixons.co.uk/',
        )
    search_url = 'http://www.dixons.co.uk/gbuk/s_action/search_keywords/index.html'

    keywords = ['Sagemcom']

    products = [
        'http://www.dixons.co.uk/gbuk/humax-hdr-fox-t2-freeview-hd-recorder-500gb-07289192-pdt.html',
        'http://www.dixons.co.uk/gbuk/humax-hdr-fox-t2-freeview-hd-recorder-1tb-11502291-pdt.html',
        'http://www.dixons.co.uk/gbuk/humax-foxsat-hdr-freesat-hd-recorder-500gb-09785361-pdt.html',
        'http://www.dixons.co.uk/gbuk/panasonic-dmr-hw100-freeview-hd-recorder-320gb-10112707-pdt.html',
        'http://www.dixons.co.uk/gbuk/samsung-smt-s7800-freesat-hd-recorder-500gb-09933610-pdt.html',
        'http://www.dixons.co.uk/gbuk/sagemcom-rti-90-320-freeview-hd-recorder-320gb-05326751-pdt.html',
        'http://www.dixons.co.uk/gbuk/humax-pvr-9300t-500-freeview-recorder-500-gb-12290868-pdt.html',
        'http://www.dixons.co.uk/gbuk/sony-svr-hdt500-freeview-hd-recorder-500gb-10209414-pdt.html',
        'http://www.dixons.co.uk/gbuk/philips-picopix-ppx2480-pico-projector-12127328-pdt.html',
        'http://www.dixons.co.uk/gbuk/philips-picopix-ppx2055-pico-projector-12127320-pdt.html',
        'http://www.dixons.co.uk/gbuk/microvision-showwx-hdmi-pico-projector-12041449-pdt.html',
        'http://www.dixons.co.uk/gbuk/sagemcom-rti-95-320-freeview-hd-recorder-320-gb-14134720-pdt.html',
        'http://www.dixons.co.uk/gbuk/sagemcom-rti95-500-freeview-hd-recorder-500-gb-13406864-pdt.html',
        'http://www.dixons.co.uk/gbuk/philips-hdtp-8530-freeview-hd-recorder-500-gb-13985229-pdt.html',
        ]

    def start_requests(self):
        for keyword in self.keywords:
            data = {
                'subaction': 'keyword_search',
                'search-field': keyword
            }
            url = self.search_url
            request = FormRequest(url, formdata=data, callback=self.parse_search)
            yield request

        for url in self.products:
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        url = response.url

        name = hxs.select("//div[@class='box-header']/h1[@class='prd-name']/text()").extract()
        if not name:
            logging.error("ERROR! NO NAME! %s" % url)
            return
        name = name[0]

        price = hxs.select("//div[@class='box-header']/div[@class='prd-amount-group']/p[@class='prd-amount']/text()").extract()
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
        base_url = get_base_url(response)
        # parse pages
        pages = hxs.select("//div[@class='pagination top']//a/@href").extract()
        for page in pages:
            request = Request(urljoin_rfc(base_url, page), callback=self.parse_search)
            yield request

        # parse products
        items = hxs.select("//div[@class='search-result']/form/ul/li")
        for item in items:
            name = item.select("div[@class='prd-infos']/a/p[@class='prd-name']/strong/text()").extract()
            if not name:
                continue
            name = name[0]
            url = item.select("div[@class='prd-infos']/a/@href").extract()
            if not url:
                logging.error("ERROR! NO URL! URL: %s. NAME: %s" % (response.url, name))
                continue
            url = url[0]
            price = item.select("div[@class='prd-actions']/p[@class='prd-amount']/strong/text()").extract()
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
