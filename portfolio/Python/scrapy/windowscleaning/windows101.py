from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse

from product_spiders.items import Product
from productloader import WindowsCleaningProductLoader, load_product

class Windows101(BaseSpider):
    name = 'windows101.com'
    allowed_domains = ['windows101.com', 'www.windows101.com']
    start_urls = ('http://www.windows101.com/shop',)

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        # sub products
        hxs = HtmlXPathSelector(response)
        product_links = hxs.select('//a[contains(@href, "product_info.php")]/@href').extract()
        for product_link in product_links:
            if not 'language=' in product_link:
                yield Request(product_link, callback=self.parse_product)



        product = {}
        #try:
        product['url'] = response.url

        product['description'] = hxs.select('//td[@class="pageHeading" and not(@align="right")]/text()').extract()[0]

        if product['description'] in ['Welcome, Please Sign In', "Let's See What We Have Here"]:
            return

        special_price =  hxs.select('//span[@class="productSpecialPrice"]/text()').re('\$(.*)')
        product['price'] = special_price[0] if special_price \
                                            else hxs.select('//td[@class="pageHeading"]/text()').re('\$(.*)')[0]
        product['sku'] = ''

        yield load_product(product, response)
        #except IndexError:
        #    return


    def parse(self, response):
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//table[@class="infoBoxContents"]//a[contains(@href, "cPath")]/@href').extract()
        for url in category_urls:
            if not 'language=' in url:
                yield Request(url)

        # products
        product_links = hxs.select('//a[contains(@href, "products_id") and \
                                    not(contains(@href, "reviews_id"))]/@href').extract()
        for product_link in product_links:
            if not 'language=' in product_link:
                yield Request(product_link, callback=self.parse_product)
