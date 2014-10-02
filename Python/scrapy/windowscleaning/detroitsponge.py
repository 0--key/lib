from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product
from productloader import WindowsCleaningProductLoader

class DetroitSpongeSpider(BaseSpider):
    name = 'detroitsponge.com'
    start_urls = ('http://www.detroitsponge.com/',)

    def parse(self, response):
        BASE = 'http://www.detroitsponge.com/'
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//a/@href').re('(.*c-\d+.*)')
        for url in category_urls:
            url = urljoin_rfc(BASE, url)
            yield Request(url)

        # products
        product_links = hxs.select('//a/@href').re('(.*p-\d+-.*)')
        for product_link in product_links:
            yield Request(urljoin_rfc(BASE, product_link), callback=self.parse_product)


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        # sub products
        hxs = HtmlXPathSelector(response)

        # product list
        product_list_nodes = hxs.select('//td[@class="DarkCell"]/../..')
        if product_list_nodes:
            for node in product_list_nodes:
                p = Product()
                loader = WindowsCleaningProductLoader(item=p, response=response)
                loader.add_value('url', response.url)
                try:
                    name = node.select('.//font/text()').extract()[0]
                except IndexError:
                    return
                loader.add_value('name', name)
                try:
                    price = node.select('.//span[@class="variantprice"]//text()').re('Price:.*?(\d.*)')[0]
                except IndexError:
                    price = node.select('.//span[@class="SalePrice"]//text()').re('.*?\$(\d.*)')[0]

                loader.add_value('price', price)

                try:
                    sku = node.select('.//*[contains(text(), "SKU")]/../td[2]/text()').extract()[0]
                except IndexError:
                    sku = ''
                loader.add_value('sku', sku)
                yield loader.load_item()

            return

        # compound product
        try:
            common_desc = hxs.select('//span[@class="ProductNameText"]/text()').extract()[0]
        except IndexError:
            return
        sub_products = hxs.select('//select[@name="variants"]/option')
        if sub_products:
            for node in sub_products:
                p = Product()
                loader = WindowsCleaningProductLoader(item=p, response=response)
                loader.add_value('url', response.url)

                name = common_desc + ' ' + node.select('./text()')[0].extract().split(u'\xa0')[0]
                loader.add_value('name', name)
                try:
                    price = node.select('./span/text()').re('([\d\.,]+)')[0]
                    loader.add_value('price', price)
                except IndexError:
                    continue
                yield loader.load_item()
            return

        # simple product
        p = Product()
        loader = WindowsCleaningProductLoader(item=p, response=response)
        loader.add_value('url', response.url)
        name = common_desc
        loader.add_value('name', name)
        try:
            price = hxs.select('//span[@class="variantprice"]/text()').re('.*?\$(.*)')[0]
        except IndexError:
            price = hxs.select('//span[@class="SalePrice"]/text()').re('.*?\$(.*)')[0]

        loader.add_value('price', price)
        try:
            sku = hxs.select('//td[contains(text(), "SKU")]/../td[2]/text()').extract()[0]
        except IndexError:
            sku = ''

        loader.add_value('sku', sku)
        yield loader.load_item()
  
