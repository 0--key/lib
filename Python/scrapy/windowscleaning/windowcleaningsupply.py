from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse

from product_spiders.items import Product
from productloader import WindowsCleaningProductLoader, load_product

class WindowCleaningSupplySpider(BaseSpider):
    name = 'window-cleaning-supply.com'
    allowed_domains = ['www.window-cleaning-supply.com']
    start_urls = ('http://www.window-cleaning-supply.com',)

    def parse(self, response):
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//div[@class="Block CategoryList Moveable Panel"]//a/@href').extract()
        for url in category_urls:
            yield Request(url)

        #next page
        next_page = hxs.select('//div[@class="CategoryPagination"]//div[@class="FloatRight"]/a/@href').extract()
        if next_page:
            yield Request(next_page[0])

        # products
        product_links = hxs.select('//div[@class="ProductDetails"]//a/@href').extract()
        for product_link in product_links:
            yield Request(product_link, callback=self.parse_product)
        

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        
        # sub products
        hxs = HtmlXPathSelector(response)
        subproduct_urls = hxs.select('//div[@class="ProductDescriptionContainer"]//a/@href').extract()
        if subproduct_urls:
            for url in subproduct_urls:
                try:
                    yield Request(url, callback=self.parse_product)
                except ValueError:
                    pass

        product = {}
        try:
            product['url'] = response.url
            product['description'] = hxs.select('//h1/text()').extract()[0]
            product['price'] = hxs.select('//em[@class="ProductPrice VariationProductPrice"]/text()').extract()[0]
            try:
                product['sku'] = hxs.select('//div[@id="sku"]/text()').extract()[0]
            except IndexError:
                product['sku'] = ''

            yield load_product(product, response)
        except IndexError:
            return
