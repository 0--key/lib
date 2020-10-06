import os
import csv
import re

# scrapy includes
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

HERE = os.path.abspath(os.path.dirname(__file__))

# spider includes
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

# main class
class AllegroMedicalSpider(BaseSpider):

    # setup
    name = "allegromedical-jrsmedical.com" # Name must match the domain
    allowed_domains = ["allegromedical.com"]
    start_urls = ()

    def start_requests(self):
        with open(os.path.join(HERE, 'jrsmedical_products.csv')) as f:
            reader = csv.reader(f)
            reader.next()
            reader = set([row[1] for row in reader])
            url = 'http://www.allegromedical.com/browse/browseProducts.do?searchPhrase=%s'
            for row in reader:
                sku = row
                if url:
                    yield Request(url % re.sub(' ', '+', sku), meta={'sku': sku}, dont_filter=True)


# main request
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # nextPageLink = hxs.select("//img[@alt='NEXT']/../@href").extract()

        # if there is a next page...
        # if next_page:
            # yield Request(urljoin_rfc(base_url, next_page[0]))

        # iterate products
        # for product in self.parse_products(hxs, base_url):
        #    yield product

        products = hxs.select("//div[@class='category']/div[@class='cat-inside']/a/@href").extract()
        for url in products:
            yield Request(urljoin_rfc(base_url, url), meta=response.meta, callback=self.parse_product, dont_filter=True)
        if not products:
            try:
                for product in self.parse_product(response):
                    yield product
            except TypeError:
                pass


    def parse_product(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        search_sku = response.meta['sku']

        main_name = hxs.select('//span[@id="mainProductName"]/text()').extract()
        main_price = hxs.select("//dd[@class='price']/text()").extract()
        if not main_name and not main_price:
            return
        main_name = main_name[0].strip()
        main_price = main_price[0].strip()
        dec = hxs.select("//dd[@class='price']/span/text()").extract()
        if dec:
            main_price += dec[0]

        skus = []
        sku_text = hxs.select("//strong[text()='Mfg Part Number(s):']/../text()").extract()
        if sku_text:
            skus += [sku.strip() for sku in sku_text[0].split(', ')]

        sub_products = hxs.select('//select[@id="skuIdSelection"]/option')
        if sub_products:
            for p in sub_products:
                p_parts = p.select('.//text()').extract()[0].split('-')
                if p_parts[-1].strip().startswith('$'):
                    price = p_parts[-1].strip()
                else:
                    price = main_price

                sku_id = p.select('.//@value').extract()[0]
                sub_product_node = hxs.select('//input[@name="skuId" and @value="%s"]/../div' % sku_id)
                sku = None
                if sub_product_node:
                    sku = self._get_sku(sub_product_node.select('.//text()').extract()[0], skus)

                loader = ProductLoader(item=Product(), response=response)
                loader.add_value('url', response.url)
                loader.add_value('name', main_name + ' ' + ''.join(p_parts[:-1]).strip())
                loader.add_value('price', price)
                if sku:
                    loader.add_value('sku', search_sku)
                    if sku in search_sku:
                        yield loader.load_item()
        else:
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('url', response.url)
            loader.add_value('name', main_name)
            loader.add_value('price', main_price)
            if skus:
                loader.add_value('sku', search_sku)
                if any([sku in search_sku for sku in skus]):
                    yield loader.load_item()

    def _get_sku(self, product_text, skus):
        result_sku = ''
        for sku in skus:
            if product_text.lower().strip().startswith(sku.lower()):
                if len(sku) > len(result_sku):
                    result_sku = sku

        return result_sku or None