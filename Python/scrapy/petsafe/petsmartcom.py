import re

from csv import DictReader
from petsafeconfig import CSV_FILENAME

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader

import logging


class PetsmartComSpider(BaseSpider):
    """
    TODO: finish changes to CSV
    """
    name = 'petsmart.com'
    allowed_domains = ['petsmart.com']
    start_urls = ()

    site_name_csv = 'petsmart.com'

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
        add_number = response.meta['notes']
        orig_name = response.meta['name'].encode('ascii', 'ignore')

        name = hxs.select("//div[@id='prodTitle']/h1/text()").extract()
        if not name:
            logging.error('ERROR!! NO NAME!! %s "%s"' % (sku, url))
            return
        name = name[0].strip()

        if hxs.select("//ul[@id='prodOptions']/li/div[@class='stepContent']/select") or\
           hxs.select("//ul[contains(@class, 'skuList')]/li"):
            names = {}
            names_js = hxs.select("//script").re(re.compile("var sliceSkuData = {([^;]*)};", re.DOTALL))
            for name_js in names_js[0].strip().split("},"):
                prod_name, prod_num = re.search('title: "([^"]*)".*?\s([^\s]*):true', name_js).groups()
                names[prod_num] = prod_name

            products = hxs.select("//script").re(re.compile("var productSkus = {([^;]*)};", re.DOTALL))
            for prod_line in products[0].strip().split("},"):
                prod_num, price = re.search('^([^:]*).*?price:"([^"]*)"', prod_line).groups()
                prod_num = prod_num.strip()
                if prod_num == add_number:
                    product = Product()
                    loader = ProductLoader(item=product, response=response, selector=hxs)
                    loader.add_value('url', url)
                    if orig_name:
                        loader.add_value('name', orig_name)
                    elif prod_num in names:
                        loader.add_value('name', "%s %s" % (name, names[prod_num]))
                    else:
                        logging.error('ERROR!! NO ADD NAME!! %s %s "%s" "%s"' % (sku, prod_num, name, url))
                        return
                    loader.add_value('price', price)

                    loader.add_value('sku', sku)

                    yield loader.load_item()
                    return
        else:
            price = hxs.select("//p[@id='mainProductPrice']//span[contains(@class, 'ourprice')]/span[@class='price']/text()").extract()
            if not price:
                logging.error('ERROR!! NO PRICE!! %s "%s" "%s"' % (sku, name, url))
                return
            price = price[0].strip()

            product = Product()
            loader = ProductLoader(item=product, response=response, selector=hxs)
            loader.add_value('url', url)
            if orig_name:
                loader.add_value('name', orig_name)
            else:
                loader.add_value('name', name)
            loader.add_value('price', price)

            loader.add_value('sku', sku)

            yield loader.load_item()
