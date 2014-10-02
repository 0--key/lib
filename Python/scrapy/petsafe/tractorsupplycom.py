from csv import DictReader
from petsafeconfig import CSV_FILENAME

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader

import logging

import lxml.etree

class TractorsupplyComSpider(BaseSpider):
    name = 'tractorsupply.com'
    allowed_domains = ['tractorsupply.com']
    start_urls = (
        'http://www.tractorsupply.com/LocationBasedPricingCmd?storeId=10551&catalogId=10001&langId=-1&lbzipcode=37938&storeCity=KNOXVILLE&storeZip=37938&physicalStoreId=529',
    )
    site_name_csv = 'tractorsupply.com'
    index = '37932'
    shop_index = '37938'
#
#    def start_requests(self):
#        products = []
#        with open(CSV_FILENAME, 'rb') as csv_file:
#            csv_reader = DictReader(csv_file)
#            for row in csv_reader:
#                if row['Retailer'] == self.site_name_csv and row['Link'] != '':
#                    products.append((row['SKU'], row['Link'], row['Notes'], row['Name of Product'].strip().decode('utf-8')))
#        for sku, url, notes, name in products:
#            yield Request(url, self.parse, meta={'sku': sku, 'notes': notes, 'name': name}, dont_filter=True)

    def parse(self, response):
        products = []
        with open(CSV_FILENAME, 'rb') as csv_file:
            csv_reader = DictReader(csv_file)
            for row in csv_reader:
                if row['Retailer'] == self.site_name_csv and row['Link'] != '':
                    products.append((row['SKU'].strip(), row['Link'].strip(), row['Notes'].strip(), row['Name of Product'].strip().decode('utf-8')))
        for sku, url, notes, name in products:
            yield Request(
                url,
                callback=self.parse_item,
                meta={'sku': sku, 'notes': notes, 'name': name},
                dont_filter=True
            )

    def parse_item(self, response):
        url = response.url
        sku = response.meta['sku']
        notes = response.meta['notes']
        name = response.meta['name'].encode('ascii', 'ignore')

        try:
            hxs = HtmlXPathSelector(response)

            price = hxs.select("//table[@class='productDetail']//span[@id='offer_price']/text()").extract()
            if not price:
                logging.error('ERROR!! NO PRICE!! %s "%s" "%s"' % (sku, name, url))
                return
            price = price[0].strip()

            product = Product()
            loader = ProductLoader(item=product, response=response, selector=hxs)
            loader.add_value('identifier', sku)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)

            loader.add_value('sku', sku)

            yield loader.load_item()

        except lxml.etree.XMLSyntaxError:
            logging.error("Rerequesting")
            yield Request(
                url,
                callback=self.parse_item,
                meta={'sku': sku, 'notes': notes, 'name': name},
                dont_filter=True
            )
