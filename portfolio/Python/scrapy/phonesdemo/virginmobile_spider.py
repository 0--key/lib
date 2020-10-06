from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class VirginMobileSpider(BaseSpider):
    name = 'virginmobile.com'
    allowed_domains = ['virginmobile.com']
    start_urls = ['http://www.virginmobile.com/vm/payAsYouGoPhones.do']

    def parse(self, response):
        BASE_URL = 'http://www.virginmobile.com/vm/'
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="webapp_shophome_3col_spotlight"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            xpath = 'div/div/div/div/div/div/div/div/div/div[@class="inner"]/text()'
            if product.select(xpath):
                loader.add_xpath('name', xpath)
                loader.add_xpath('price', 'div/div/div/div/div/div/p/span/text()')
                relative_url = product.select('div/div/div/div/div/p/a/@href')
                if relative_url:
                    url = urljoin_rfc(BASE_URL, relative_url.extract()[0], 
                                      response.encoding)
                    loader.add_value('url', url)
            else:
                xpath = 'div/div/div/div/div/div/div/div/div/div/div[@class="inner"]/text()'
                if product.select(xpath):
                    loader.add_xpath('name', xpath)
                    loader.add_xpath('price', 'div/div/div/div/div/div/div/p/span/text()')
                    relative_url = product.select('div/div/div/div/div/div/p/a/@href')
                    if relative_url:
                        url = urljoin_rfc(BASE_URL, relative_url.extract()[0], 
                                          response.encoding)
                        loader.add_value('url', url)
            yield loader.load_item()
