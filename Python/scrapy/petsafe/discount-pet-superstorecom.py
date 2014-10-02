from csv import DictReader
from petsafeconfig import CSV_FILENAME

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import open_in_browser

from product_spiders.items import Product, ProductLoader

import logging


class DiscountPetSuperstoreComSpider(BaseSpider):
    name = 'discount-pet-superstore.com'
    allowed_domains = ['discount-pet-superstore.com']
    start_urls = ()

    site_name_csv = 'discount-pet-superstore.com'

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

        products_table = hxs.select("//body/table[@class='Box']//table/tr[translate(@bgcolor,'abcdef','ABCDEF')='#F5F5F5'] | \
                                     //body/table[@class='Box']//table/tr[td[translate(@bgcolor,'abcdef','ABCDEF')='#F5F5F5'][1] and count(td) = 4]|\
                                     //body/table[@class='Box']//table/tbody/tr[translate(@bgcolor,'abcdef','ABCDEF')='#F5F5F5'] |\
                                     //body/table[@class='Box']//table/tbody/tr[td[translate(@bgcolor,'abcdef','ABCDEF')='#F5F5F5'][1] and count(td) = 4]")

        if not products_table:
            logging.error('ERROR!! NO TABLE!! %s "%s"' % (sku, url))
            return

        for row in products_table:
            row_sku = row.select("td[1]/text()").re("[^\s]+")
            if not row_sku:
                row_sku = row.select("td[1]/div/text()").re('[^\s]+')
            if not row_sku:
                row_sku = row.select("td[1]/strong/text()").re("[^\s]+")
            if not row_sku:
                row_sku = row.select("td[1]/div/strong/text()").re("[^\s]+")
            if not row_sku:
                row_sku = row.select("td[1]/div/font/text()").re("[^\s]+")
            if not row_sku:
                logging.error('ERROR!! NO SKU!! %s "%s"' % (sku, url))
                continue
            row_sku = "".join(row_sku).strip().strip('"')
            if sku == row_sku or add_sku == row_sku:
                name = "".join([x.strip() for x in row.select("td[2]//text()").extract()]).strip()
                if not name:
                    logging.error('ERROR!! NO NAME!! %s "%s"' % (sku, url))
                    continue

                price = row.select("td[3]//span[@class='ProductTextBoldRed']//text()").re("[\d.]+")
                if not price:
                    price = row.select("td[3]//font[translate(@color,'abcdef','ABCDEF')='#FF0000']//text()").re("[\d.]+")
                if not price:
                    price = row.select("td[3]//span[contains(@style, 'color: #FF0000')]//text()").re("[\d.]+")
                if not price:
                    logging.error('ERROR!! NO PRICE!! %s "%s" "%s"' % (sku, name, url))
                    continue
                price = price[0]

                product = Product()
                loader = ProductLoader(item=product, response=response, selector=hxs)
                loader.add_value('url', url)
                loader.add_value('name', name)
                loader.add_value('price', price)

                loader.add_value('sku', sku)

                yield loader.load_item()
                return

        logging.error('ERROR!! PRODUCT NOT FOUND!! %s "%s"' % (sku, url))
