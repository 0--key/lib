from csv import DictReader
from petsafeconfig import CSV_FILENAME

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader

import logging


class PetstreetmallComSpider(BaseSpider):
    name = 'petstreetmall.com'
    allowed_domains = ['petstreetmall.com']
    start_urls = ()

    site_name_csv = 'petstreetmall.com'

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
        sec_sku = response.meta['notes']
        name = response.meta['name'].encode('ascii', 'ignore')

        main_product = hxs.select("//div[@id='Product-MainProduct']")
        main_products = hxs.select("//div[@id='Product-MainProductContainer']//div[@class='Product-SubProduct']")
        secondary_products = hxs.select("//div[@id='Product-SubProductContainer']//div[@class='Product-SubProduct']")

        main_product_sku = main_product.select("div[@id='Product-lblItem']/span[@id='lblItem']/text()").extract()
        if not main_product_sku:
            logging.error("NO MAIN SKU! %s" % url)
        else:
            main_product_sku = main_product_sku[0]

        if main_product_sku == sku or main_product_sku == sec_sku:
            # extract main product
            price = main_product.select(".//div[@class='Product-Price']/span[@id='lblClubPrice']/b/font/text()").re("\$(.*)")
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
            return
        elif main_products:
            for product in main_products:
                product_sku = product.select("div[@class='Product-SubProductNumber']/font/text()").re("#(.+)")
                if not product_sku:
                    logging.error("NO MAIN SKU! %s" % url)
                else:
                    product_sku = product_sku[0]

                if product_sku == sku or product_sku == sec_sku:
                    # extract secondary product
                    price = product.select(".//span[contains(@id, 'lblClubPrice')]/b/font/text()").re("\$(.*)")
                    if not price:
                        logging.error('ERROR!! NO SEC PRICE!! %s "%s" "%s"' % (sku, name, url))
                        return
                    price = price[0].strip()

                    product = Product()
                    loader = ProductLoader(item=product, response=response, selector=hxs)
                    loader.add_value('url', url)
                    loader.add_value('name', name)
                    loader.add_value('price', price)

                    loader.add_value('sku', sku)

                    yield loader.load_item()
                    return
        elif secondary_products:
            for product in secondary_products:
                product_sku = product.select("div[@class='Product-SubProductNumber']/text()").re("#(.+)")
                if not product_sku:
                    logging.error("NO SECONDARY SKU! %s" % url)
                else:
                    product_sku = product_sku[0]

                if product_sku == sku or product_sku == sec_sku:
                    # extract secondary product
                    price = product.select(".//span[contains(@id, 'lblClubPrice2')]/b/font/text()").re("\$(.*)")
                    if not price:
                        logging.error('ERROR!! NO SEC PRICE!! %s "%s" "%s"' % (sku, name, url))
                        return
                    price = price[0].strip()

                    product = Product()
                    loader = ProductLoader(item=product, response=response, selector=hxs)
                    loader.add_value('url', url)
                    loader.add_value('name', name)
                    loader.add_value('price', price)

                    loader.add_value('sku', sku)

                    yield loader.load_item()
                    return
        else:
            logging.error("No products found!")
