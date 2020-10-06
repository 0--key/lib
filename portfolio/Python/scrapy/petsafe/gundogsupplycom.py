from csv import DictReader
from petsafeconfig import CSV_FILENAME

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader

import logging


class GundogsupplyComSpider(BaseSpider):
    name = 'gundogsupply.com'
    allowed_domains = ['gundogsupply.com']
    start_urls = ()

    site_name_csv = 'gundogsupply.com'

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
        sec_number = response.meta['notes']

        name = hxs.select("//h1[contains(@class, 'hheadline')]/text()").extract()
        if not name:
            logging.error('ERROR!! NO NAME!! %s "%s"' % (sku, url))
            return
        name = name[0].strip()

        price = hxs.select("//div[@class='orderblock']/form/div[@class='orderblock-big']/b/font/text()").extract()
        if not price:
            options = hxs.select("//div[@class='dummies']")
            for option in options:
                add_name = option.select("strong[1]/text()").extract()
                if not add_name:
                    logging.error('ERROR!! NO ADD NAME!! %s "%s"' % (sku, url))
                    continue
                add_name = add_name[0]
                add_number = option.select("font[@color='gray']/text()").extract()
                if not add_number:
                    logging.error('ERROR!! NO ADD NUMBER!! %s "%s"' % (sku, url))
                    continue
                add_number = add_number[0]
                price = option.select("b[1]/text()").extract()
                if not price:
                    logging.error('ERROR!! NO ADD PRICE!! %s "%s"' % (sku, url))
                    continue
                price = price[0]

                if sec_number == add_number:
                    product = Product()
                    loader = ProductLoader(item=product, response=response, selector=hxs)
                    loader.add_value('url', url)
                    loader.add_value('name', add_name)
                    loader.add_value('price', price)

                    loader.add_value('sku', sku)

                    yield loader.load_item()

        else:
            price = price[0].strip()

            product = Product()
            loader = ProductLoader(item=product, response=response, selector=hxs)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)

            loader.add_value('sku', sku)

            yield loader.load_item()
