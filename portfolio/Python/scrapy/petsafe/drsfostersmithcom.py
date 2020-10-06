from __future__ import with_statement
import re

from csv import DictReader
from petsafeconfig import CSV_FILENAME

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader

import logging

class DrsfostersmithComSpider(BaseSpider):
    name = 'drsfostersmith.com'
    allowed_domains = ['drsfostersmith.com']
    start_urls = ()

    site_name_csv = 'drsfostersmith.com'

    def start_requests(self):
        products = []
        with open(CSV_FILENAME, 'rb') as csv_file:
            csv_reader = DictReader(csv_file)
            for row in csv_reader:
                if row['Retailer'] == self.site_name_csv and row['Link'] != '':
                    products.append((row['SKU'].strip(), row['Link'].strip(), row['Notes'].strip(), row['Name of Product'].strip().decode('utf-8')))
        for sku, url, notes, name in products:
            yield Request(url, self.parse, meta={'sku': sku, 'notes': notes, 'name': name}, dont_filter=True)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        url = response.url
        sku = response.meta['sku']
        name = response.meta['name'].encode('ascii', 'ignore')
        sec_number = response.meta['notes']

        prod_name = hxs.select("//h1[contains(@class, 'categoryname')]/text()").extract()
        if not prod_name:
            logging.error('ERROR!! NO NAME!! %s "%s"' % (sku, url))
            return
        prod_name = prod_name[0].strip()

        options = hxs.select("//tr[td/input[@type='radio']]")

        found_products = []

        for option in options:
            text = option.select("td[2]/div[1]/span/text()").extract()
            if not text:
                logging.error("OPTIONS TEXT NOT FOUND! '%s'" % url)
                continue
            text = "".join(text)
            m = re.search("([^,]*),([^,]*)", text)
            if not m:
                logging.error("CAN'T PARSE OPTIONS TEXT! '%s', '%s'" % (text, url))
                continue

            add_name = m.group(1).strip()
            add_number = m.group(2).strip()

            price = option.select('.//span[@class="productSave"]/text()').extract()
            if not price:
                price = option.select("td[2]/div[2]/span/text()").extract()
            if not price:
                price = option.select("td[2]/div[1]/span[2]/text()").extract()
            if not price:
                logging.error('ERROR!! NO PRICE!! %s "%s" "%s"' % (sku, prod_name, url))
                return
            price = price[0].strip()

            found_products.append(("%s %s" % (prod_name.encode('ascii', 'ignore'), add_name), add_number, price))

            if add_number == sec_number:
                product = Product()
                loader = ProductLoader(item=product, response=response, selector=hxs)
                loader.add_value('url', url)
                loader.add_value('name', name)
                loader.add_value('price', price)

                loader.add_value('sku', sku)

                yield loader.load_item()
                return

        with open("/home/juraseg/src/drsfostersmith_products.txt", 'a+') as handle:
            handle.write("======================================\n")
            handle.write("Product not found\n")
            handle.write("SKU: %s, Name: %s\n" % (sku, name))
            for prod in found_products:
                handle.write("Found: %s, %s, %s\n" % prod)
            handle.write("======================================\n\n")