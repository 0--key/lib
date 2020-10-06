from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product
from productloader import WindowsCleaningProductLoader

from scrapy.http import FormRequest

class CWCSupplyUSA(BaseSpider):
    name = 'cwcsupplyusa.com'
    allowed_domains = ['cwcsupplyusa.com', 'www.cwcsupplyusa.com']
    start_urls = ('http://www.cwcsupplyusa.com',)

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        # sub products
        hxs = HtmlXPathSelector(response)

        name = hxs.select('//div[@id="product-detail-div"]//select/@name').extract()
        subproducts = hxs.select('//div[@id="product-detail-div"]//select/option')
        if name and 'size' not in response.meta:
            subproducts = subproducts[1:]
            for subproduct in subproducts:
                request = FormRequest.from_response(response, formdata={name[0]: subproduct.select('./@value').extract()},
                                                    dont_click=True, callback=self.parse_product)
                request.meta['size'] = subproduct.select('./text()').extract()[0].strip()
                yield request
            return

        product = Product()
        loader = WindowsCleaningProductLoader(item=product, response=response)
        #try:
        #product['url'] = response.url
        loader.add_value('url', response.url)
        name = hxs.select('//div[@id="product-detail-div"]//h1/text()').extract()[0].strip()

        if 'size' in response.meta:
            name += ' ' + response.meta['size']

        loader.add_value('name', name)

        special_price =  hxs.select('//span[@class="prod-detail-sale-value"]/text()').extract()
        price = special_price[0] if special_price\
                                            else hxs.select('//span[@class="prod-detail-cost-value"]/text()') \
                                                    .extract()[0]
        loader.add_value('price', price)
        
        try:
            sku = hxs.select('//span[@class="prod-detail-man-part-value"]/text()').extract()[0]
        except IndexError:
            sku = ''

        loader.add_value('sku', sku)

        yield loader.load_item()
        #except IndexError:
        #    return


    def parse(self, response):
        URL_BASE = 'http://www.cwcsupplyusa.com'
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//td[@class="module-body"]/ul[@class="module-list cat-nav"]//li/a/@href').extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        #next page
        next_page = hxs.select('//a[@class="pager-link"]/@href').extract()
        if next_page:
            yield Request(next_page[0])

        # products
        product_links = hxs.select('//img[@src="/themes/default-1-1-1-1/images/buttons/cart_btn_view.gif"]/../@href')\
                           .extract()
        for product_link in product_links:
            product_link = urljoin_rfc(URL_BASE, product_link)
            yield Request(product_link, callback=self.parse_product)
