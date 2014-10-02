import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

from scrapy import log

class FragrancenetSpider(BaseSpider):
    name = 'fragrancenet.com'
    allowed_domains = ['fragrancenet.com']
    start_urls = ('http://www.fragrancenet.com/f/net/view_all.html?locale=en_US',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        brands = hxs.select('//div[@class="descolumn"]//a/@href').extract()
        for brand in brands:
            yield Request(brand)

        next_page = hxs.select('//a[@class="next active"]/@href').extract()
        if next_page:
            yield Request(next_page[0])

        for product in self.parse_products(hxs, response):
            yield product

    def parse_products(self, hxs, response):
        products = hxs.select('//div[@class="productList clear"]//div[starts-with(@class, "promoCell")]')

        for p in products:
            loader = ProductLoader(item=Product(), selector=p)

            name = p.select('.//p[@class="para1"]//text()').extract()
            name = ' '.join([n.strip() for n in name])
            name = re.sub(' +', ' ', name)

            loader.add_xpath('url', './/a[starts-with(@class, "border")]/@href')
            loader.add_value('name', name)
            loader.add_xpath('sku', './/p[@class="border"]/text()', re='Item: (.*)')
            loader.add_xpath('price', './/p[@class="para3"]/text()', re='Our Price: (.*)')

            if not loader.get_output_value('price'):
                yield Request(loader.get_output_value('url'), callback=self.parse_products2)
                continue



            if not p.select('.//p[@class="para3"]/text()').re('Our Price: (.*)')[0].startswith('$')\
               and response.meta.get('ret', 0) < 3:

                yield Request(response.url, dont_filter=True, meta={'ret': response.meta.get('ret', 0) + 1})
                return

            yield loader.load_item()

    def parse_products2(self, response):
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//div[@class="item"]//td[@class="col1"]/..')

        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_value('url', response.url)
            loader.add_xpath('name', './/p[@class="para1"]/text()')
            loader.add_xpath('price', './/p[@class="ourPrice"]/following-sibling::p/strong/text()')
            loader.add_xpath('sku', './/p[@class="para2"]/text()', re='item #(.*)')

            price = product.select('.//p[@class="ourPrice"]/following-sibling::p/strong/text()').extract()[0]
            if not price.startswith('$') and response.meta.get('ret', 0) < 3:
                yield Request(response.url, dont_filter=True,
                              meta={'ret': response.meta.get('ret', 0) + 1},
                              callback=self.parse_products2)
                return

            yield loader.load_item()
