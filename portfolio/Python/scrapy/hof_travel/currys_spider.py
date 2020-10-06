import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

import logging

class CurrysSpider(BaseSpider):
    name = 'currys.co.uk-travel'
    allowed_domains = ['currys.co.uk']
    start_urls = ['http://www.currys.co.uk/gbuk/search-keywords/xx_xx_xx_xx_xx/travel/xx-criteria.html']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        URL_BASE = get_base_url(response)

        categories = hxs.select("//nav[contains(@class, 'section_nav')]/ul/li//a/@href").extract()
        for url in categories:
            url = urljoin_rfc(URL_BASE, url)
            request = Request(url, callback=self.parse)
            yield request

        pages = hxs.select("//ul[@class='pagination']//a/@href").extract()
        for url in pages:
            url = urljoin_rfc(URL_BASE, url)
            request = Request(url, callback=self.parse)
            yield request

        items = hxs.select("//article[contains(@class, 'product')]/div[contains(@class, 'desc')]")
        for item in items:
            name = item.select(".//div/header[@class='productTitle']/a/text()").extract()
            if not name:
                continue
            name = name[0].strip()
            name = re.sub("[\s]+", " ", name)

            url = item.select(".//div/header[@class='productTitle']/a/@href").extract()
            if not url:
                logging.error("ERROR! NO URL! URL: %s. NAME: %s" % (response.url, name))
                continue
            url = url[0]
            price = item.select(".//div//span[@class='currentPrice']/ins/text()").extract()
            if not price:
                logging.error("ERROR! NO PRICE! URL: %s. NAME: %s" % (response.url, name))
                continue
            price = price[0].strip()

            l = ProductLoader(item=Product(), response=response)
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()

