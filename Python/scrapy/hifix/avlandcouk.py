import logging
import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class AvlandCoUkSpider(BaseSpider):
    name = 'avland.co.uk'
    allowed_domains = ['avland.co.uk']
    brands_url = 'http://www.avland.co.uk/brands/'
    products_url = 'http://www.avland.co.uk/products/'

    def start_requests(self):
        yield Request(self.brands_url, callback=self.parse_brands)
        yield Request(self.products_url, callback=self.parse_products)

    def parse_brands(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # categories
        for url in hxs.select('//body/div/center/table[position()>1]//a/@href').extract():
            url = urljoin_rfc(URL_BASE, url.strip())
            yield Request(url, callback=self.parse_brand)

    def parse_products(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # products list
        products = hxs.select("//tr[@class='btna']")
        for product_el in products:
            url = product_el.select("td[3]/a//@href").extract()
            if not url:
                url = product_el.select("td[4]/a//@href").extract()
                every_10th = True
                if not url:
                    logging.error("ERROR!! NO URL 2!! %s" % response.url)
                    continue
            else:
                every_10th = False
            url = url[0]
            url = urljoin_rfc(URL_BASE, url)

            if every_10th:
                name = product_el.select("td[3]//text() | td[4]/a//text()").extract()
            else:
                name = product_el.select("td[2]//text() | td[3]/a//text()").extract()
            if not name:
                logging.error("ERROR!! NO NAME 2!! %s %s" % response.url)
                continue
            name = " ".join(name).strip()

            price = product_el.select("td[last()]/font/text()").extract()
            if not price:
                logging.error("ERROR!! NO PRICE 2!! %s %s" % (response.url, name))
                continue
            price = price[0]

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            yield loader.load_item()

        if not products:
            # search for subcategories
            for url in hxs.select('//div/center/table[3]//a/@href').extract():
                url = urljoin_rfc(URL_BASE, url.strip())
                yield Request(url, callback=self.parse_products)

    def parse_brand(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # products list
        products = hxs.select('//body/div/center/table[position()>2]//a/@href').extract()
        for url in products:
            url = urljoin_rfc(URL_BASE, url.strip())
            yield Request(url, callback=self.parse_item)

    def parse_item(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        options = hxs.select("//select[@onchange='this.form.submit()']/option/@value").extract()

        if ('do_not_use_options' in response.meta and response.meta['do_not_use_options']) or not options:
            product_el1 = hxs.select("//body/div/center/div")
            product_el2 = hxs.select("//body/div/center")

            name = product_el1.select("table[1]/tr[2]/td[1]//font[1]/text()").extract()
            product_el = product_el1
            if not name:
                name = product_el2.select("table[1]/tr[2]/td[1]//font[1]/text()").extract()
                product_el = product_el2
                if not name:
                    name = product_el1.select("center/table[1]/tr[2]/td[1]//font[1]/text()").extract()
                    product_el = product_el1
                    if not name:
                        name = product_el1.select("center/table[1]/tr[2]/td[1]//font[1]/text()").extract()
                        product_el = product_el2
                        if not name:
                            name = product_el1.select("table[1]/tr[1]/td[1]//font[1]/text()").extract()
                            product_el = product_el1
                            if not name:
                                logging.error("ERROR!!! No name! %s" % response.url)
                                return
            name = name[0]

            url = response.url

            prices = product_el.select(".//span[@id='span1']/table/tr[1]")
            products_found = 0
            for price_text in prices.select(".//text()").extract():
                m = re.search('\xa3([^\s]+?)[\s]+(.*?)$', price_text)
                if m:
                    prod_name = name + " " + m.group(2)
                    price = m.group(1)
                    product = Product()
                    loader = ProductLoader(item=product, response=response)
                    loader.add_value('url', url)
                    loader.add_value('name', prod_name.strip())
                    loader.add_value('price', price)
                    yield loader.load_item()
                    products_found += 1

            if not prices:
                price = hxs.select("//text()").re(u'\xa3([\d.]*)')
                if price:
                    if 'add_name' in response.meta:
                        name += " " + response.meta['add_name']
                    product = Product()
                    loader = ProductLoader(item=product, response=response)
                    loader.add_value('url', url)
                    loader.add_value('name', name.strip())
                    loader.add_value('price', price)
                    yield loader.load_item()
                    products_found += 1

            if not products_found:
                logging.error("ERROR!!! No prices! %s" % response.url)
        elif options:
#            options = hxs.select("//select[@onchange='this.form.submit()']/option/@value").extract()
            if options:
                for option in options:
                    formdata = {
                        'items': '1',
                        'p1': option
                    }
                    url = hxs.select("//form[@id='update']/@action").extract()[0]
                    url = urljoin_rfc(URL_BASE, url)
                    yield FormRequest(url, formdata=formdata, callback=self.parse_item, dont_filter=True,
                        meta={
                            'do_not_use_options': True,
                            'add_name': option
                        })


