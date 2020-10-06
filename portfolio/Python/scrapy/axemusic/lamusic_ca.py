import re
import logging
import urllib

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class LaMusicCaSpider(BaseSpider):
    name = 'lamusic.ca'
    allowed_domains = ['lamusic.ca']
    start_urls = ('http://www.lamusic.ca',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[@id="display_menu_s"]/ul/li/a/@href').extract():
            yield Request(url + '?searching=Y&show=4000&page=1', callback=self.parse_product_list)

    def parse_product_list(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//a[contains(@class,"subcategory_link")]/@href').extract():
            yield Request(url + '?searching=Y&show=4000&page=1', callback=self.parse_product_list)

        for url in hxs.select(u'//a[contains(@class,"productnamecolor")]/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        product_loader = ProductLoader(item=Product(), selector=hxs)
        product_loader.add_value('url', response.url)
        product_loader.add_xpath('name', u'//span[@itemprop="name"]/text()')
        product_loader.add_xpath('price', u'//form[@id="vCSS_mainform"]//span[@itemprop="price"]/text()')
        product_loader.add_xpath('sku', u'//span[@class="product_code"]/text()')
        product_loader.add_xpath('category', u'//td[@class="vCSS_breadcrumb_td"]//a[position()=2]/@title')
        product_loader.add_xpath('image_url', u'concat("http:",//img[@id="product_photo"]/@src)')
        product_loader.add_xpath('brand', u'//meta[@itemprop="manufacturer"]/@content')
        if hxs.select(u'//img[@class="vCSS_img_icon_free_shipping"]'):
            product_loader.add_value('shipping_cost', '0')
        
        product = product_loader.load_item()
        if hxs.select(u'//tr[@class="Multi-Child_Background"]'):
            for opt in hxs.select(u'//tr[@class="Multi-Child_Background"]'):
                p = Product(product)
                p['sku'] = opt.select(u'./td[1]/text()').extract()[0].strip()
                p['name'] = opt.select(u'./td[2]/text()').extract()[0].strip()
                p['price'] = opt.select(u'./td[4]//span[@itemprop="price"]/text()').extract()[0].strip().replace('$', '').replace(',', '')
                yield p
        else:
            yield product
