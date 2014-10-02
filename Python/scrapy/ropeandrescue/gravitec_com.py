import re
import logging

from decimal import Decimal
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

def multiply(lst):
    if not lst:
        return [('', 0)]

    while len(lst) > 1:
        result = []
        for name0, price0 in lst[0]:
            for name1, price1 in lst[1]:
                result.append((name0 + ' ' + name1, float(price0) + float(price1)))
        lst = [result] + lst[2:]
    # Dynamic list
    if not lst[0]:
        return [('', 0)]
    return lst[0]

class GravitecSpider(BaseSpider):
    name = 'gravitec.com'
    allowed_domains = ['gravitec.com']
    start_urls = ('http://www.gravitec.com/equipment/confined-space/bluewater-safeline-nfpa-rope/rop-bl-5346/',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[@id="subnav"]/ul[1]/li/a/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            # NOTE: viewall to skip pagination
            yield Request(url + '?viewall=true', callback=self.parse_product_list)

    def parse_product_list(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[contains(@class,"catdesc")]/a/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        opt_groups = []
        def fix_options(o):
            try:
                return (o[0].strip(), o[1].replace(',', ''))
            except:
                return (o[0].strip(), '0')

        for option in hxs.select(u'//div[@id="proddimensions"]//select'):
            opt_list = option.select(u'./option[position() != 1]/text()').extract()
            opt_list = [o.split(' - $') for o in opt_list]
            opt_groups.append([fix_options(o) for o in opt_list])

        for opt_name, opt_price in multiply(opt_groups):
            product_loader = ProductLoader(item=Product(), selector=hxs)
            product_loader.add_value('url', response.url)
            product_loader.add_xpath('name', u'//h1/text()')
            product_loader.add_xpath('price', u'//div[@id="prodprice"]/text()')
            product_loader.add_xpath('sku', u'substring-after(//div[@id="itemnum"]/text(),"#")')
            product_loader.add_xpath('category', u'normalize-space(//div[@id="breadcrumbs"]/a[3]/text())')
            img = hxs.select(u'//img[@id="prodimg"]/@src').extract()[0]
            img = urljoin_rfc(get_base_url(response), img)
            product_loader.add_value('image_url', img)
#        product_loader.add_xpath('brand', u'substring-after(//div[@class="product-meta"]/span[contains(text(),"Manufacturer:")]/text(),":")')
            product_loader.add_value('shipping_cost', '')

            product = product_loader.load_item()
            product['name'] = (product['name'] + ' ' + opt_name).strip()
            if float(opt_price) != 0:
                product['price'] = Decimal(opt_price)

            # Dynamic select of second-level options
            if len(opt_groups) == 2 and len(opt_groups[1]) == 0:
                select1 = hxs.select(u'//div[@id="proddimensions"]//select')[0]
                for option in select1.select(u'./option'):
                    product_new = Product(product)
                    opt_name = option.select(u'./text()').extract()[0]
                    opt_value = option.select(u'./@value').extract()[0]
                    opt_id = select1.select(u'./@onchange').extract()[0].split("'")[1]

                    product_new['name'] = (product_new['name'] + ' ' + opt_name.strip()).strip()
                    yield Request('http://www.gravitec.com/za/GVT/products/includes/selection-dimensions.jsp?&dim=1&refid=' + opt_id + '&dim0=' + opt_value,
                            meta={'product': product_new}, callback=self.parse_price)
            else:
                yield product

    def parse_price(self, response):
        hxs = HtmlXPathSelector(response)
        product = response.meta['product']

        for option in hxs.select(u'//select/option[position() != 1]/text()').extract():
            name, price = option.split(' - $')
            product_new = Product(product)

            product_new['name'] = (product_new['name'] + ' ' + name.strip()).strip()
            product_new['price'] = price.split()[0].replace(',', '').strip()
            yield product_new

