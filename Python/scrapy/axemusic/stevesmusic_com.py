import re
import logging
import urllib

from decimal import Decimal
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class StevesMusicComSpider(BaseSpider):
    name = 'stevesmusic.com'
    allowed_domains = ['stevesmusic.com']
    start_urls = ('http://www.stevesmusic.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//ul[@class="boxListing"]/li/a/@href').extract():
            yield Request(url, callback=self.parse_product_list)

    def parse_product_list(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[@class="categoryListBoxContents"]/a/@href').extract():
            yield Request(url, callback=self.parse_product_list)

        for url in hxs.select(u'//h3[@class="itemTitle"]/a/@href').extract():
            yield Request(url, callback=self.parse_product)

        next_page = hxs.select(u'//div[@id="productsListingListingTopLinks"]/a[contains(@title,"Next Page")]/@href').extract()
        if next_page:
            yield Request(next_page[0], callback=self.parse_product_list)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        product_loader = ProductLoader(item=Product(), selector=hxs)
        product_loader.add_value('url', response.url)
        product_loader.add_xpath('name', u'//h1[@id="productName"]/text()')
        if hxs.select(u'//h2[@id="productPrices"]/span[@class="productSpecialPrice"]/text()'):
            product_loader.add_xpath('price', u'substring-after(//h2[@id="productPrices"]/span[@class="productSpecialPrice"]/text(),"C")')
        else:
            product_loader.add_xpath('price', u'substring-after(//h2[@id="productPrices"]/text(),"C")')

#        product_loader.add_xpath('sku',
#                u'''normalize-space(substring-after(//ul[@id="productDetailsList"]/li[contains(text(),"Steve's Code")]/text(),":"))''')
        # many products don't have steeve's code
        product_id = [x.split('=')[1] for x in response.url.split('&') if x.startswith('products_id=')][0]
        product_loader.add_value('sku', product_id)

#        product_loader.add_xpath('category', u'//div[@id="categoryIcon"]/a/text()')
        product_loader.add_xpath('category', u'//span[@class="category-subs-parent"]/text()')

        img = hxs.select(u'//div[@id="productMainImage"]/noscript/a/img/@src').extract()
        if img:
            img = urljoin_rfc(get_base_url(response), img[0])
            product_loader.add_value('image_url', img)
        product_loader.add_xpath('brand',
                u'normalize-space(substring-after(//ul[@id="productDetailsList"]/li[contains(text(),"Manufactured")]/text(),":"))')

        product = product_loader.load_item()
        if hxs.select(u'//div[@class="wrapperAttribsOptions"]'):
            opts = hxs.select(u'//div[@class="wrapperAttribsOptions"]/div//label/text()').extract()
            if not opts:
                opts = hxs.select(u'//div[@class="wrapperAttribsOptions"]/div//option/text()').extract()
            for opt in opts:
                p = Product(product)
                try: 
                    if '$' in opt:
                        name, price = opt.split('(')[:2]
                    else:
                        name, price = opt, None
                except: name, price = opt, None
                p['name'] = p['name'] + ' ' + name.strip()
                if price:
                    pricen = price.replace(')', '').replace('C', '').replace('$', '').replace(',', '').strip()
                    if pricen.startswith('+'):
                        p['price'] = p['price'] + Decimal(pricen[1:])
                    else:
                        p['price'] = Decimal(pricen)
                yield p
        # http://www.stevesmusic.com/index.php?main_page=product_info&cPath=2_27_103&products_id=7059 ?
        else:
            yield product
