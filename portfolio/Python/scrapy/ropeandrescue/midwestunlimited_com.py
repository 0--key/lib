import re
import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class MidWestUnlimitedComSpider(BaseSpider):
    name = 'midwestunlimited.com'
    allowed_domains = ['midwestunlimited.com']
    start_urls = ('http://www.midwestunlimited.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[contains(@class,"nav_categories")]/ul/li/a/@href').extract():
            yield Request(url, callback=self.parse_cats)

    def parse_cats(self, response):
        hxs = HtmlXPathSelector(response)

        cats = hxs.select(u'//ul[contains(@class,"ProductGroups")]/li/div[1]/a/@href').extract()
        if cats:
            for url in cats:
                yield Request(url, callback=self.parse_product_list)
        else:
            for x in self.parse_product_list(response):
                yield x

    def parse_product_list(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[contains(@class,"ProductTitle")]//a/@href').extract():
            yield Request(url, callback=self.parse_product)

        next_url = hxs.select(u'//div[contains(@class,"CategoryPagination")]/span/a[contains(text(),"Next")]/@href').extract()
        if next_url:
            yield Request(next_url[0], callback=self.parse_product_list)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        product_loader = ProductLoader(item=Product(), selector=hxs)
        product_loader.add_value('url', response.url)
        product_loader.add_xpath('name', u'//h2/text()')
        product_loader.add_xpath('price', u'//em[contains(@class,"ProductPrice")]/text()')
        product_loader.add_xpath('sku', u'//span[@class="VariationProductSKU"]/text()')
        product_loader.add_xpath('category', u'//div[@id="ProductBreadcrumb"]/ul/ul/li[2]/a/text()')
        product_loader.add_xpath('image_url', u'//div[@class="ProductThumbImage"]/a/img/@src')
        product_loader.add_xpath('brand', u'//div[@class="Value"]/a/text()')
        product_loader.add_value('shipping_cost', '')


        options = hxs.select(u'//div[@class="DetailRow"]//ul/li/label/input/../..')
        if options:
            product_id = hxs.select(u'//input[@name="product_id"]/@value').extract()[0]
            product_orig = product_loader.load_item()
            for opt in options:
                name = opt.select(u'.//input/../text()[2]').extract()
                if not name:
                    name = opt.select(u'concat(.//input/../span[1]/text(),.//input/../span[2]/text())').extract()
                var = opt.select(u'.//input/@value').extract()

                product = Product(product_orig)
                product['name'] = (product['name'] + ' ' + name[0].strip()).strip()
                yield Request('http://www.midwestunlimited.com/remote.php' +
                        '?w=GetVariationOptions&productId=' + product_id + '&options=' + var[0],
                        meta={'product': product}, callback=self.parse_price)
        else:
            yield product_loader.load_item()

    def parse_price(self, response):
        product = response.meta['product']

        data = eval(response.body, {'true':True, 'false':False})
        product['price'] = data['price'].replace(',', '').replace('$', '')
        if data['sku']:
            product['sku'] = data['sku']
        product['image_url'] = data['image'].replace('\\', '')

        yield product
