from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

class WebstaurantStoreSpider(BaseSpider):
    name = 'webstaurantstore.com'
    allowed_domains = ['webstaurantstore.com']
    start_urls = ('http://www.webstaurantstore.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        '''
        categories = hxs.select('//ul[@class="side_menu bolded" and position()=1]/li[not(@class)]/a/@href').extract()
        for cat in categories:
            yield Request(cat)

        subcategories = hxs.select('//a[@class="category_name"]/@href').extract()
        for subcat in subcategories:
            yield Request(urljoin_rfc(get_base_url(response), subcat))
        '''
        categories = ['http://www.webstaurantstore.com/vendor/CAR150/cardinal-international.html',
                      'http://www.webstaurantstore.com/vendor/LIB500/libbey.html',
                      'http://www.webstaurantstore.com/vendor/VOL300/vollrath.html',
                      'http://www.webstaurantstore.com/vendor/RUS600/dexter-russell.html',
                      'http://www.webstaurantstore.com/vendor/GET600/get-enterprises.html',
                      'http://www.webstaurantstore.com/vendor/BEV500/beverage-air.html']

        for cat in categories:
            yield Request(cat)

        next_page = hxs.select('//a[@title="Next page"]/@href').extract()
        if next_page:
            yield Request(urljoin_rfc(get_base_url(response), next_page[0]))

        products = hxs.select('//td[@class="search_product_title"]/a/@href').extract()
        for product in products:
            yield Request(urljoin_rfc(get_base_url(response), product), callback=self.parse_product)

    def parse_product(self, response):
        compound = [product for product in self._parse_compound_product(response)]
        if compound:
            for product in compound:
                yield product
            return

        loader = ProductLoader(response=response, item=Product())
        loader.add_xpath('name', '//h1[@itemprop="Name"]//text()')
        loader.add_xpath('price', '//input[@name="price"]/@value')
        loader.add_value('url', response.url)
        loader.add_xpath('sku', '//span[@itemprop="model"]/text()')
        yield loader.load_item()

    def _parse_compound_product(self, response):
        hxs = HtmlXPathSelector(response)
        main_name = hxs.select('//h1[@itemprop="Name"]//text()').extract()[0]
        skus = hxs.select('//div[@id="details"]//b[contains(text(),' +
                          '"Item Numbers")]/following-sibling::text()').extract()
        
        if skus:
            skus = skus[0]
            skus = [sku.strip() for sku in skus.split(',')]
        for i, option in enumerate(hxs.select('//select[@id="item_number"]/option[contains(text(), "$")]/text()').extract()):
            loader = ProductLoader(response=response, item=Product())
            name, price = option.split('-')
            loader.add_value('name', main_name.strip() + ' ' + name.strip())
            loader.add_value('price', price)
            loader.add_value('url', response.url)
            if len(skus) > i:
                loader.add_value('sku', skus[i])

            yield loader.load_item()
