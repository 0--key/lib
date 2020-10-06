from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class JagtdirektDkSpider(BaseSpider):
    name = 'jagtdirekt.dk'
    allowed_domains = ['jagtdirekt.dk']
    start_urls = ('http://jagtdirekt.dk',)

    def parse_sub(self, response):
        hxs = HtmlXPathSelector(response)

        main_name = hxs.select(u'//h1/text()').extract()[0]
        for item in hxs.select(u'//tr[@class="ProductInfoDotedTop"]'):
            product_loader = ProductLoader(item=Product(), selector=item)

            name = u' '.join(item.select(u'.//td[contains(@class,"main")]//b/text()').extract())
            product_loader.add_value('name', main_name + ' / ' + name)

            price = item.select(u'.//span[@class="js_price_tax"]/text()').extract()[0]
            price = price.strip().replace('.', '').replace(',', '.')
            product_loader.add_value('price', price)

            product_loader.add_value('url', response.url)

            yield product_loader.load_item()
 
    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for item in hxs.select(u'//tr[contains(@class,"product-item")]'):
            product_loader = ProductLoader(item=Product(), selector=item)

            product_loader.add_xpath('name', u'.//td[@class="productListingNewName"]/b/a/text()')

            price = item.select(u'.//span[@class="js_price_tax"]/text()').extract()[0]
            price = price.strip().replace('.', '').replace(',', '.')
            product_loader.add_value('price', price)

            url = item.select(u'.//td[@class="productListingNewName"]/b/a/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)

            # If quantity field is not present on page, there are subproducts
            qty = item.select(u'.//input[@name="products_qty"]').extract()
            if qty:
                yield product_loader.load_item()
            else:
                yield Request(url, callback=self.parse_sub)

        level = response.meta.get('level', 1)
        sub_url = u'//div[@class="box-content"]/' + u'/'.join([u'ul/li'] * level) + '/a/@href'
        subcategories = hxs.select(sub_url).extract()
 
        for subcategory in subcategories:
            url = urljoin_rfc(get_base_url(response), subcategory)
            yield Request(url, meta={'level': level+1})

        next_url = hxs.select(u'//li[@class="page-next"]/a/@href').extract()
        if next_url:
            next_url = urljoin_rfc(get_base_url(response), next_url[0])
            yield Request(next_url, meta={'level': level})
