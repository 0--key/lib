from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse

from product_spiders.items import Product
from productloader import WindowsCleaningProductLoader, load_product

class ShopWindowCleaningResourceSpider(BaseSpider):
    name = 'shopwindowcleaningresource.com'
    start_urls = ('http://www.shopwindowcleaningresource.com',)

    def parse(self, response):
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//div[@class="header-nav"]//a/@href').extract()
        for url in category_urls:
            yield Request(url)

        #next page
        next_page = hxs.select('//a[@class="next"]/@href').extract()
        if next_page:
            yield Request(next_page[0])
            
        # products
        product_links = hxs.select('//h3[@class="product-name"]/a/@href').extract()
        for product_link in product_links:
            yield Request(product_link, callback=self.parse_product)


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        # sub products
        hxs = HtmlXPathSelector(response)

        # compound product
        sub_products = hxs.select('//table[@id="super-product-table"]//tr')
        if sub_products:
            sub_products = sub_products[1:]
            for p in sub_products:
                product = {}
                product['url'] = response.url
                product['description'] = p.select('td[1]//text()').extract()[0]
                product['price'] = ''.join(p.select('td[2]//text()').extract()).strip()
                product['sku'] = ''
                yield load_product(product, response)

            return

        product = {}
        try:
            product['url'] = response.url
            product['sku'] = ''
            product['description'] = hxs.select('//div[@class="product-name"]/h2/text()').extract()[0]

            try:
                product['price'] = hxs.select('//div[@class="product-shop"]//p[@class="special-price"]/span[2]/text()')\
                                      .extract()[0]
            except IndexError:
                product['price'] = hxs.select('//div[@class="product-shop"]//span[@class="regular-price"]/span/text()')\
                                      .extract()[0]

            yield load_product(product, response)
        except IndexError:
            return
  
