from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class GuitarGuitarSpider(BaseSpider):
    name = 'guitarguitar.co.uk'
    allowed_domains = ['guitarguitar.co.uk']
    start_urls = ['http://www.guitarguitar.co.uk/brands/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        relative_urls = hxs.select('//div[@class="az_brand"]/div/a/@href').extract()
        for relative_url in relative_urls:
            url = urljoin_rfc('http://www.guitarguitar.co.uk/',
                              relative_url, response.encoding)
            yield Request(url, callback=self.parse_page)

    def parse_page(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="list_item"]')
        names = [p.select('a/strong/text()').extract()[0].strip()+ ' ' +p.select('a/text()').extract()[1].strip() for p in products]

        urls = [p.select('a/@href').extract()[0].strip() for p in products]
        product_prices = hxs.select('//div[@class="list_item_price"]')
        prices = [p.select('span/strong/text()').extract()[0] for p in product_prices]
        list_prod = zip(names, urls, prices)
        dict_prod = [dict(name=prod[0],url=prod[1],price=prod[2]) for prod in list_prod]
        for product in dict_prod:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_value('name', product['name'])
            loader.add_value('url', 'http://www.guitarguitar.co.uk/'+product['url'])
            #xpath = 'div[@class="price-box"]/span[@class="regular-price"]/span[@class="price"]/text()'
            #if product.select(xpath):
            #    price = product.select(xpath).extract()[0]
            #else:
            #    xpath = 'div[@class="price-box"]/p[@class="special-price"]/span[@class="price"]/text()'
            #    if product.select(xpath):
            #        price = product.select(xpath).extract()[0]
            loader.add_value('price', product['price'])
            yield loader.load_item()
        next_page = hxs.select('//div/div/div/div/strong/a/@href').extract()
        if next_page:
            relative_url = next_page[-1]
            next_url = urljoin_rfc('http://www.guitarguitar.co.uk/',
                              relative_url, response.encoding)
            yield Request(next_url, callback=self.parse_page)


