import re
import logging
import urllib

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class RopeAndRescueComSpider(BaseSpider):
    name = 'ropeandrescue.com'
    allowed_domains = ['ropeandrescue.com']
    start_urls = ('http://www.ropeandrescue.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[@class="SideCategoryListFlyout"]/ul/li/a/@href').extract():
            if 'sale-items' in url:
                continue
            yield Request(url, callback=self.parse_product_list)

    def parse_product_list(self, response):
        hxs = HtmlXPathSelector(response)

        category = hxs.select(u'//h1/text()').extract()[0]

        for url in hxs.select(u'//div[contains(@class,"CategoryDescription")]/table[1]//a/@href').extract():
            yield Request(url, meta={'category': category}, callback=self.parse_product_list)
        for url in hxs.select(u'//div[contains(@class,"ProductImage")]/a/@href').extract():
            yield Request(url, meta={'category': response.meta.get('category', category)}, callback=self.parse_product)

        next_page = hxs.select(u'//div[@class="CategoryPagination"]/div/a[contains(text(),"Next")]/@href').extract()
        if next_page:
            yield Request(next_page[0], callback=self.parse_product_list)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        options = hxs.select(u'//table[@class="ropetable" or @class="dbitable"]//td/a/@href').extract()
        if not options:
            options = hxs.select(u'//table//a/@href').extract()
            options = [o for o in options if o.startswith(response.url.rstrip('/'))]
        if options:
            for url in options: 
                yield Request(url, meta=response.meta, callback=self.parse_product)
            return

        product_loader = ProductLoader(item=Product(), selector=hxs)
        product_loader.add_value('url', response.url)
        product_loader.add_xpath('name', u'//h1/text()')
        product_loader.add_xpath('price', u'//em[contains(@class,"ProductPrice")]/text()')
        product_loader.add_xpath('sku', u'//div[@id="sku"]/text()')
        product_loader.add_value('category', response.meta['category'])
        product_loader.add_xpath('image_url', u'//div[@class="ProductThumbImage"]//img/@src')
        product_loader.add_xpath('brand', u'//div[@class="DetailRow"]/div/a/text()')
        product_loader.add_xpath('shipping_cost', u'//div[@class="DetailRow"]/div[contains(text(),"Shipping")]/../div[2]/text()')

        options = hxs.select(u'//div[@class="productAttributeList"]//ul/li/label/input/../../..')
        options2 = hxs.select(u'//div[@class="productAttributeList"]//select')
        # FIXME http://www.ropeandrescue.com/conterra-tac-longbow-ranger-rescue-pack/
        # checkbox support?
        product_id = hxs.select(u'//input[@name="product_id"]/@value').extract()[0]
        product_orig = product_loader.load_item()

        if options:
            for opt in options:
                names = opt.select(u'.//input/../span/text()').extract()
                values = opt.select(u'.//input/@value').extract()
                value_names = opt.select(u'.//input/@name').extract()
                for i in xrange(len(names)):
                    product = Product(product_orig)
                    product['name'] = (product['name'] + ' ' + names[i].strip()).strip()
                    yield Request('http://www.ropeandrescue.com/remote.php' +
                            '?w=getProductAttributeDetails&product_id=' + product_id +
                            '&' + urllib.quote(value_names[i]) + '=' + values[i],
                            meta={'product': product}, callback=self.parse_price)
        elif options2:
            names = options2.select(u'./option[@value!=""]/text()').extract()
            values = options2.select(u'./option[@value!=""]/@value').extract()
            value_name = options2.select(u'./@name').extract()[0]
            for i in xrange(len(names)):
                product = Product(product_orig)
                product['name'] = (product['name'] + ' ' + names[i].strip()).strip()
                yield Request('http://www.ropeandrescue.com/remote.php' +
                        '?w=getProductAttributeDetails&product_id=' + product_id +
                        '&' + urllib.quote(value_name) + '=' + values[i],
                        meta={'product': product}, callback=self.parse_price)
 
        else:
            yield product_loader.load_item()

    def parse_price(self, response):
        product = response.meta['product']

        data = eval(response.body, {'true':True, 'false':False})
        product['price'] = data['details']['price'].replace(',', '').replace('$', '')
        product['sku'] = data['details']['sku']

        yield product
