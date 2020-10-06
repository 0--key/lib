import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

import logging

class CurrysSpider(BaseSpider):
    name = 'currys.co.uk-electricals'
    allowed_domains = ['currys.co.uk']
    start_urls = ["http://www.currys.co.uk/gbuk/toasters/336_3157_30245_xx_xx/xx-criteria.html",
                  "http://www.currys.co.uk/gbuk/kettles/336_3156_30244_xx_xx/xx-criteria.html",
                  "http://www.currys.co.uk/gbuk/household-appliances/small-kitchen-appliances/coffee-machines-and-accessories-3159-m.html",
                  "http://www.currys.co.uk/gbuk/household-appliances/small-kitchen-appliances/small-cooking-appliances-3155-m.html",
                  "http://www.currys.co.uk/gbuk/household-appliances/small-kitchen-appliances/food-preparation-3164-m.html",
                  "http://www.currys.co.uk/gbuk/household-appliances/small-kitchen-appliances/food-preparation-3164-m.html",
                  "http://www.currys.co.uk/gbuk/household-appliances/small-kitchen-appliances/food-preparation-3164-m.html",
                  "http://www.currys.co.uk/gbuk/household-appliances/small-kitchen-appliances/food-preparation-3164-m.html",
                  "http://www.currys.co.uk/gbuk/upright-vacuum-cleaners/337_3168_30256_xx_xx/xx-criteria.html",
                  "http://www.currys.co.uk/gbuk/cylinder-vacuum-cleaners/337_3169_30257_xx_xx/xx-criteria.html",
                  "http://www.currys.co.uk/gbuk/handheld-vacuum-cleaners/337_3170_30258_xx_xx/xx-criteria.html",
                  "http://www.currys.co.uk/gbuk/wet-dry-cleaners/337_3171_30259_xx_xx/xx-criteria.html",
                  "http://www.currys.co.uk/gbuk/irons/338_3173_30261_xx_xx/xx-criteria.html",
                  "http://www.currys.co.uk/gbuk/steam-generator-irons/338_3174_30262_xx_xx/xx-criteria.html",
                  "http://www.currys.co.uk/gbuk/home-appliances/fans-air-conditioning-340-c.html"]

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