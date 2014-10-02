from csv import DictReader
from petsafeconfig import CSV_FILENAME

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader

import logging


class AmazonComPetsafeSpider(BaseSpider):
    name = 'amazon.com_petsafe'
    allowed_domains = ['amazon.com']
    start_urls = ()

    site_name_csv = 'amazon.com'

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

        name = hxs.select("//h1[contains(@class, 'parseasinTitle')]/span/text()").extract()
        if not name:
            logging.error('ERROR!! NO NAME!! %s "%s"' % (sku, url))
            return
        name = name[0].strip()

        price = hxs.select("//table[@class='product']//span[@id='actualPriceValue']/b/text()").extract()
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
