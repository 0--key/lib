from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import ProductLoader, Product

import logging

class WholesalegadgetpartsComSpider(BaseSpider):
    name = 'wholesalegadgetparts.com'
    allowed_domains = ['wholesalegadgetparts.com']
    start_urls = (
        'https://www.wholesalegadgetparts.com/home.php',
        )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        categories = hxs.select("//div[@id='left-bar']/\
                                   div[@class='menu-dialog menu-categories-list']/\
                                   div[@class='content']//a/@href").extract()
        for category in categories:
            url = urljoin_rfc(base_url, category)
            yield Request(url, callback=self.parse)

        sub_categories = hxs.select("//div[@id='center-main']/div[@class='subcategories']/a/@href").extract()
        for category in sub_categories:
            url = urljoin_rfc(base_url, category)
            yield Request(url, callback=self.parse)

        items_table = hxs.select("//div[@id='center-main']/div[@class='dialog']/div[@class='content']/table")
        rows = items_table.select("tr")
        i = 0
        rows_count = len(rows)
        while i < rows_count:
            name_row = rows.pop(0)
            image_row = rows.pop(0)
            empty_row = rows.pop(0)
            price_row = rows.pop(0)
            order_row = rows.pop(0)
            for name_cell, price_cell in zip(name_row.select('td'), price_row.select('td')):
                name = name_cell.select("a/text()").extract()
                if not name:
                    logging.error("%s - ERROR! NO NAME!" % response.url)
                    continue
                name = name[0]
                url = name_cell.select("a/@href").extract()
                if not url:
                    logging.error("%s - ERROR! NO URL!" % response.url)
                    continue
                url = url[0]
                url = urljoin_rfc(base_url, url)
                price = price_cell.select("div[@class='price-row']/span/text()").extract()
                if not price:
                    logging.error("%s - ERROR! NO PRICE!" % response.url)
                    continue
                price = price[0]
                l = ProductLoader(item=Product(), response=response)
                l.add_value('identifier', str(name))
                l.add_value('name', name)
                l.add_value('url', url)
                l.add_value('price', price)
                yield l.load_item()
            i += 5

