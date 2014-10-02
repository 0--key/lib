import re

from csv import DictReader
from petsafeconfig import CSV_FILENAME

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader

import logging


class PetcoComSpider(BaseSpider):
    name = 'petco.com'
    allowed_domains = ['petco.com']
    start_urls = ()

    site_name_csv = 'petco.com'

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
        add_sku = response.meta['notes']
        prod_name = response.meta['name']

        name = hxs.select("//div[@class='product-details']/h1/text()").extract()
        if not name:
            logging.error('ERROR!! NO NAME!! %s "%s"' % (sku, url))
            return
        name = name[0].strip()

        price = hxs.select("//div[@class='product-details']/div[@id='InternetPrice']/p/\
                              span[@class='attentionInternetSale']/text()").extract()
        if not price:
            logging.error('ERROR!! NO PRICE!! %s "%s" "%s"' % (sku, name, url))
            return
        price = price[0].strip()

        options = hxs.select("//div[contains(@class, 'relative')]")

        if len(options) > 1:
            take_name = True
        else:
            take_name = False

        for option in options:
            prod_sku = option.select("p[@class='prod-detail-spec']/text()").extract()
            if not prod_sku:
                logging.error('ERROR!! NO SKU!! %s "%s" "%s"' % (sku, name, url))
                continue
            m = re.search("SKU:(.*)$", prod_sku[-1], re.DOTALL)
            prod_sku = m.group(1).strip()
            if prod_sku == add_sku:
                if prod_name:
                    name = prod_name
                else:
                    if take_name:
                        add_name = option.select("p[@class='prod-detail-spec']/strong[1]/text()").extract()
                        if not add_name:
                            logging.error('ERROR!! NO ADD NAME!! %s "%s" "%s"' % (sku, name, url))
                            return
                        name = "%s %s" % (name, add_name[0].strip())
                price = option.select("div[@class='prod-detail-spec2']/span[@class='attention'][last()]/text()").extract()
                if not price:
                    logging.error('ERROR!! NO ADD PRICE!! %s "%s" "%s"' % (sku, name, url))
                    return
                price = price[0].strip()
                product = Product()
                loader = ProductLoader(item=product, response=response, selector=hxs)
                loader.add_value('url', url)
                loader.add_value('name', name.encode('ascii', 'ignore'))
                loader.add_value('price', price)

                loader.add_value('sku', sku)

                yield loader.load_item()
                return

        logging.error("Product not found: '%s' '%s' - '%s'" % (sku, add_sku, url))

