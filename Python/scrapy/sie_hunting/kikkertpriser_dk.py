from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class KikkertpriserDkSpider(BaseSpider):
    name = 'kikkertpriser.dk'
    allowed_domains = ['kikkertpriser.dk']
    start_urls = ('http://www.kikkertpriser.dk/',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for item in hxs.select(u'//td[@class="Description_ProductList"]'):
            product_loader = ProductLoader(item=Product(), selector=item)

            product_loader.add_xpath('name', u'.//a/@title')

            price = item.select(u'../..//span[@class="Price_Productlist"]/text()').extract()[0]
            price = price.strip().rstrip(' DKK').replace('.', '').replace(',', '.')
            if price == u'Ring for pris!':
                price = 0
            product_loader.add_value('price', price)

            url = item.select(u'.//a/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)

            yield product_loader.load_item()

        level = response.meta.get('level', 1)
        sub_url = u'//table[@id="ProductMenu_Table"]/../' + u'/'.join([u'table/tr/td'] * level) + '/a/@href'
        subcategories = hxs.select(sub_url).extract()
 
        for subcategory in subcategories:
            url = urljoin_rfc(get_base_url(response), subcategory)
            yield Request(url, meta={'level': level+1})
