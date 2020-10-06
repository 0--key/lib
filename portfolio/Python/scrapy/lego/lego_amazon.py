import csv
import os
import copy

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http.cookies import CookieJar

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class AmazonSpider(BaseSpider):
    name = 'lego-amazon.com'
    allowed_domains = ['amazon.com']

    def start_requests(self):
        with open(os.path.join(HERE, 'products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['sku']
                url = 'http://www.amazon.it/s/ref=nb_sb_noss_1?' + \
                      'url=search-alias%%3Dtoys&field-keywords=lego+%s&x=0&y=0'

                yield Request(url % sku, meta={'sku': sku})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@id="atfResults"]//div[starts-with(@id, "result_0")]')
        pr = None
        search_results = []
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', './/*[contains(@class, "Title") or contains(@class, "title")]//a/text()')
            loader.add_xpath('url', './/*[contains(@class, "Title") or contains(@class, "title")]//a/@href')
            price = product.select('.//*[@class="newPrice"]//span[contains(@class,"price")]/text()').extract()
            if not price:
                price = product.select('.//div[@class="usedNewPrice"]//span[@class="price"]/text()').extract()
            if price:
                loader.add_value('price', price[0].replace(',','.'))
            loader.add_value('sku', response.meta['sku'])
            loader.add_value('identifier', response.meta['sku'])
            pr = loader
            search_results.append(pr)

        if search_results:
            cur_prod = search_results[0]
            next_prods = search_results[1:]
            yield Request(cur_prod.get_output_value('url'), callback=self.parse_product,meta={'cur_prod': cur_prod}, dont_filter=True)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        cur_prod = response.meta['cur_prod']
        product_desc = hxs.select('//div[@class="buying" and @style="padding-bottom: 0.75em;"]').extract()
        matched = False
        if product_desc:
            if "Venduto e spedito da <b>Amazon.it</b>" in product_desc[0].strip().replace('\n',''):
                matched = True
        if not matched:
            cur_prod.add_value('name',cur_prod.get_output_value('name') + ' - 3rd party')
        yield cur_prod.load_item()