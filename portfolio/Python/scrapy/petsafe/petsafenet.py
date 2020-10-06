from csv import DictReader
from petsafeconfig import SKU_CSV_FILENAME

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader

import logging


class PetsafeNetSpider(BaseSpider):
    name = 'petsafe.net'
    allowed_domains = ['petsafe.net']
    start_urls = ()

    search_url = 'http://www.petsafe.net/search?q='

    def start_requests(self):
        skus = []
        with open(SKU_CSV_FILENAME, 'rb') as csv_file:
            csv_reader = DictReader(csv_file)
            for row in csv_reader:
                if row['SKU'] not in skus:
                    skus.append(row['SKU'])
        logging.error("Number of products: %d" % len(skus))
        for sku in skus:
            url = self. search_url + sku
            yield Request(url, self.parse, meta={'sku': sku}, dont_filter=True)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        url = response.url
        sku = response.meta['sku']

        products = hxs.select("//ul[@id='categoryproductWrapper']/li/div")
        for product in products:
            prod_sku = product.select(".//div[@class='modelNumber']/text()").extract()
            if not prod_sku:
                logging.error('ERROR!! NO NAME!! %s "%s"' % (sku, url))
                return
            prod_sku = prod_sku[0].strip()

            if prod_sku == sku:
                name = product.select("header/a/text()").extract()
                if not name:
                    logging.error('ERROR!! NO NAME!! %s "%s"' % (sku, url))
                    return
                name = name[0].strip()

                url = product.select("header/a/@href").extract()
                if not url:
                    logging.error('ERROR!! NO url!! %s "%s"' % (sku, url))
                    return
                url = url[0].strip()

                price = product.select(".//div[@class='descPrice']/div/text()").extract()
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
                break
