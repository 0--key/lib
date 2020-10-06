from scrapy.spider import BaseSpider

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader

import logging

class FratellistrazzulloItSpider(BaseSpider):
    name = "fratellistrazzullo.it"
    allowed_domains = ["fratellistrazzullo.it"]
    start_urls = (
        'http://www.fratellistrazzullo.it/',
        )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        categories = hxs.select("//div[@id='box_left_ctl02_livello_box']//table[@class='tabellaMenu']/tr/td[2]/a/@href").extract()
        for category in categories:
            yield Request(category, callback=self.parse)

        pages = hxs.select("//div[@id='box_center2_span_navigazione']/a/@href").extract()
        for page in pages:
            yield Request(page, callback=self.parse)

        items = hxs.select("//td[@class='centerPagina']/div[@id='box_center_ctl01_livello_box']/div[@class='tabMargini']/\
                              table[@class='tabellaBoxCentrale']/tr[2]/td/table/tr/td/table/tr/td/a/@href |\
                            //td[@class='centerPagina']/div[@id='box_center2_box_catalogo']/\
                              table[@class='tabellaBoxCentrale']/tr[2]/td/table/tr/td/table/tr/td/a/@href").extract()
        for item in items:
            yield Request(item, callback=self.parse_item)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//td[@class='centerPagina']/div[@class='tabMargini']/table[@class='tabellaBoxCentrale']/form/tr[2]/td/table/tr/td[2]")
        name = content.select("//td[@class='centerPagina']/div[@class='tabMargini']/table[@class='tabellaBoxCentrale']/form/tr[1]/td/h1[@class='titolo']/text()").extract()
        if not name:
            logging.error("NO NAME!")
            return
        name = name[0]
        url = response.url
                 
        # adding product
        price = content.select("span[@id='box_center_span_prezzo']/span[@class='prezzo']/strong/text()").extract()
        if not price:
            logging.error("NO PRICE")
            return
        price = price[0]

        l = ProductLoader(item=Product(), response=response)
        l.add_value('identifier', name.encode('ascii', errors='ignore'))
        l.add_value('name', name)
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()
