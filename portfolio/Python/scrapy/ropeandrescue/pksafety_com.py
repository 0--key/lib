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
    return lst[0]

class PkSafetyComSpider(BaseSpider):
    name = 'pksafety.com'
    allowed_domains = ['pksafety.com']
    start_urls = ('http://www.pksafety.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[@class="catNav"]/ul/li/div/a/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product_list)

    def parse_product_list(self, response):
        hxs = HtmlXPathSelector(response)

        cats = hxs.select(u'//div[@id="RightColumn"]/table/tr/td/center/div[@class="contentsName"]/a/@href').extract()
        if cats:
            for url in cats:
                if url.split('.')[-1].lower() not in ('htm', 'html'):
                    # Contains links to PDFs as well
                    continue
                url = urljoin_rfc(get_base_url(response), url)
                yield Request(url, callback=self.parse_product_list)
        else:
            opt_groups = []
            def fix_options(what, o):
                try:
                    return (what + ':' + o[0], o[1].replace(',', ''))
                except:
                    return (what + ':' + o[0], '0')

            for option in hxs.select(u'//div[@class="eyOptions"]//select'):
                what = option.select(u'./@name').extract()[0]
                opt_list = option.select(u'./option[@value!="PleaseSelect" and @value!="Please Select"]/text()').extract()
                opt_list = [o.replace(')', '').split('(') for o in opt_list]
                opt_groups.append([fix_options(what, o) for o in opt_list])

            for opt_name, opt_price in multiply(opt_groups):
                product_loader = ProductLoader(item=Product(), selector=hxs)
                product_loader.add_value('url', response.url)
                product_loader.add_xpath('name', u'//h1/text()')
                if hxs.select(u'//div[@class="bigSalePrice"]'):
                    product_loader.add_xpath('price', u'//div[@class="bigSalePrice"]/span/font/text()')
                elif hxs.select(u'//span[@class="bigSalePrice"]'):
                    product_loader.add_xpath('price', u'//span[@class="bigSalePrice"]/font/text()')
                else:
                    product_loader.add_xpath('price', u'//div[@class="itemRegPrice"]/span/font/text()')

                product_loader.add_xpath('sku', u'normalize-space(substring-after(//div[@class="code"]/text(),":"))')
                product_loader.add_xpath('category', u'//div[@class="eyBreadcrumbs"]/a[2]/text()')
                product_loader.add_xpath('image_url', u'//img[@id="SwitchThisImage"]/@src')
#            product_loader.add_xpath('brand', u'substring-after(//div[@class="product-meta"]/span[contains(text(),"Manufacturer:")]/text(),":")')
                product_loader.add_value('shipping_cost', '')

                product = product_loader.load_item()
                product['name'] = (product['name'] + ' ' + opt_name).strip()
                product['price'] = product['price'] + Decimal(opt_price)
                yield product
