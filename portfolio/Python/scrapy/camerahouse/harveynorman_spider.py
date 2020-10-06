import csv
import os
import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class HarveyNormanSpider(BaseSpider):
    name = 'harveynorman.com.au'
    allowed_domains = ['harveynorman.com.au']
    start_urls = ['http://www.harveynorman.com.au/endecasearch/result']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//ul[@class="hlisting category section inset cnr bdr cfx"]/li[@class="item  cfx" or @class="item last cfx" or @class="item first clear"]')
        if products:
            logging.error("INFO! FOUND PRODUCTS: %d" % len(products))
            for product in products:
                price = product.select('div/div/div/div/div/span[@class="configurable-price-from-label"]/text()')
                if price:
                   url = product.select('div/div/a[@class="name fn"]/@href').extract()[0]
                   logging.error("OPTIONS! SENT!")
                   yield Request(url, callback=self.parse_product)
                else:
                    loader = ProductLoader(item=Product(), selector=product)
                    loader.add_xpath('name', 'div/div/a[@class="name fn"]/strong/text()')
                    name = product.select('div/div/a[@class="name fn"]/strong/text()').extract()
                    loader.add_xpath('url', 'div/div/a[@class="name fn"]/@href')
                    price = product.select('div/div/div/span/span[@class="price"]/text()').extract()
                    if price:
                        price = price[0]
                    else:
                        price = product.select('div/div/div/div/span/span[@class="price"]/text()').extract()
                        if price:
                            price = price[0]
                        else:
                            price = product.select('div/div/div/span/span[@class="after cfx"]/span[@class="price"]/text()').extract()
                            if price:
                                price = price[0]
                            else:
                                continue
#                                logging.error("ERROR! PRODUCT PARSE ERROR! NO PRICE. %s - %s" % (response.url, name))
    
                    loader.add_value('price', price)
                    yield loader.load_item()
        else:
            logging.error("ERROR! PRODUCTS NOT FOUND!")
        search_params = hxs.select('//*[@id="btn-show-more"]/@onclick').extract()
        if search_params:
            url = 'http://www.harveynorman.com.au/endecasearch/result/ajaxShowMore?' + search_params[0].split("'")[1] + '&mode=list'
            yield Request(url)

    def parse_product(self, response):
        logging.error("OPTIONS! ARRIVED!")
        hxs = HtmlXPathSelector(response)
        loader = ProductLoader(item=Product(), response=response)
        loader.add_xpath('name', '//*[@id="content"]/div/div/h2/span[@class="product-name"]/text()')
        loader.add_value('url', response.url)
        price = hxs.select('//*[@id="product-view-price"]/div/div/span/span/text()').extract()
        if price:
            price = price[0]
        else:
            price = hxs.select('//*[@id="product-view-price"]/div/div/div/span/span[@class="price"]/text()')
            if price:
                price = price[0]
            else:
                return
#            else:
#                logging.error("ERROR! PRODUCT PARSE ERROR! NO PRICE. %s" % (response.url, ))
        loader.add_value('price', price)
        yield loader.load_item()
           
