import re

try:
    import json
except ImportError:
    import simplejson as json

from csv import DictReader
from petsafeconfig import CSV_FILENAME

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader

import logging


class CabelasComSpider(BaseSpider):
    name = 'cabelas.com'
    allowed_domains = ['cabelas.com']
    start_urls = ()

    site_name_csv = 'cabelas.com'

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

        name = hxs.select("//div[@id='productInfo']/div[@class='labledContainer']/\
                             h1[@class='label']/text()").extract()
        if not name:
            logging.error('ERROR!! NO NAME!! %s "%s"' % (sku, url))
            return
        name = name[0].strip()

        options_select = hxs.select("//div[@class='variantConfigurator']//select[@class='js-dropdown']")

        if options_select:
            options = hxs.select("//div[@class='variantConfigurator']/form/div/script[last()]/text()").extract()
            options = options[0]
            options = re.search("ddWidgetEntries\[[^]]*\] = ([^;]*);", options).group(1)
            options = options.replace("'", '"').replace('id', '"id"', ).\
                replace('values', '"values"').replace('labels', '"labels"')
            options = json.loads(options)
            found = False
            for option in options:
                if option['values'][0] == response.meta['notes']:
                    found = True

                    label = option['labels'][0]
                    price = re.search("\$[\d.]+", label).group(0)
                    add_name = re.search("(.+) - (.+) - (.+)", label).group(1)

                    product = Product()
                    loader = ProductLoader(item=product, response=response, selector=hxs)
                    loader.add_value('url', url)
                    loader.add_value('name', name + " " + add_name)
                    loader.add_value('price', price)

                    loader.add_value('sku', sku)

                    yield loader.load_item()

            if not found:
                logging.error('ERROR!! OPTION NOT FOUDN! %s "%s" "%s"' % (sku, name, url))
                logging.error("ID: %s. OPTIONS: %s" % (response.meta['notes'], str(options)))

        else:
            price = hxs.select("//div[@id='productInfo']//div[@class='price']/dl/dd[1]/text()").extract()
            if not price:
                logging.error('ERROR!! NO PRICE!! %s "%s" "%s"' % (sku, name, url))
                return
            price = price[0].strip()

            product = Product()
            loader = ProductLoader(item=product, response=response, selector=hxs)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)

            loader.add_value('sku', sku)

            yield loader.load_item()
