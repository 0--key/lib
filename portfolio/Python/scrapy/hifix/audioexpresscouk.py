import re
import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class AudioExpressCoUkSpider(BaseSpider):
    name = 'audio-express.co.uk'
    allowed_domains = ['audio-express.co.uk']
    start_urls = ('http://audio-express.co.uk',)

    def parse(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # categories
        category_urls = hxs.select('//div[@id="menuBar"]//@onclick').re("JavaScript:window\.location\.assign\('([^']*?)'\);")
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        # product
        products = hxs.select("//div[@id='mainProdWrapper']//div[@id='prodTitlesWrapper']")
        for product in  products:
            loader = ProductLoader(item=Product(), selector=product)
            name = product.select(".//div[@id='prodTitles']//text()").extract()
            if not name:
                logging.error("ERROR!! NO NAME!! %s" % response.url)
                continue
            name = " ".join(name)

            url =  response.url
            loader.add_xpath('price', ".//div[@id='prodPrices']/div[@class='priceHD']//text()", re='\xa3(.*)')
            loader.add_xpath('price', ".//div[@id='prodPrices']/div[@class='priceRRP']/text()", re='\xa3(.*)')
            loader.add_value('url', url)
            loader.add_value('name', name)
            yield loader.load_item()

        # products list
        products2 = hxs.select("//div[@id='content']//div[@id='mainListWrapper']/ul/li/div[last()]")
        for product_el in products2:
            loader = ProductLoader(item=Product(), selector=product_el)
            name = product_el.select("div[@class='catName']/div[@class='productNameOnly']/a/text()").extract()
            if not name:
                logging.error("ERROR!! NO NAME!! %s" % response.url)
                continue
            name = name[0]

            name2 = product_el.select("div[@class='catName']/div[@class='productDescOnly']/a/text()").extract()
            if not name2:
                continue
            name += " " + " ".join(name2)

            name3 = product_el.select("div[@class='catImage']/div[@class='catFinishBox']/text()").extract()
            if not name3:
                continue
            name += " " + name3[0]

            url = product_el.select("div[@class='catName']/div[@class='productNameOnly']/a/@href").extract()
            if not url:
                logging.error("ERROR!! NO URL!! %s %s" % (response.url, name))
                continue
            url = urljoin_rfc(URL_BASE, url[0])

            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_xpath('price', "div[@class='HDbox']//div[@class='BS_HDsm']/text()", re='\xa3(.*)')
            loader.add_xpath('price', "div[@class='HDbox']//div[@class='BS_RRPsm']/text()", re='\xa3(.*)')
            yield loader.load_item()

        products3 = hxs.select("//div[@id='content']//div[@id='mainListWrapper']/div[@class='hotWrapper linkcell']")
        for product_el in products3:
            loader = ProductLoader(item=Product(), selector=product_el)
            name = product_el.select(".//div[@class='hotName']/div/div/div[1]//text()").extract()
            if not name:
                logging.error("ERROR!! NO NAME!! %s" % response.url)
                continue
            name = " ".join(name)

            url = product_el.select("@onclick").re("JavaScript:window\.location\.assign\('([^']*?)'\);")
            if not url:
                logging.error("ERROR!! NO URL!! %s %s" % (response.url, name))
                continue
            url = urljoin_rfc(URL_BASE, url[0])

            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_xpath('price', ".//div[@class='priceHD']//text()", re='\xa3(.*)')
            loader.add_xpath('price', ".//div[@class='priceRRP']/text()", re='\xa3(.*)')
            yield loader.load_item()

        products4 = None
        if not products3:
            products4 = hxs.select("//div[@id='content']//div[@id='mainListWrapper']//a/@href").extract()
            for url in products4:
                url = urljoin_rfc(URL_BASE, url)
                yield Request(url)

        if not products and not products2 and not products3 and not products4:
            logging.error("ERROR!! NO PRODUCTS!! %s " % response.url)