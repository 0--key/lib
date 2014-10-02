from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import ProductLoader, Product

import logging

login = 'cmonitor'
password = 'cprcompetition123'

class CprFranchiseComSpider(BaseSpider):
    name = 'cpr-franchise.com'
    allowed_domains = ['cpr-franchise.com']
    start_urls = (
        'http://cpr-franchise.com/online-store/error_message.php?need_login',
        )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        login_form = hxs.select("//form[@name='errorform']")
        login_post_url = login_form.select("@action").extract()[0]
        login_form_data = {}
        for input_el in login_form.select("input"):
            input_name = input_el.select("@name").extract()[0]
            input_value = input_el.select("@value").extract()[0]
            login_form_data[input_name] = input_value
        login_form_data['username'] = login
        login_form_data['password'] = password
        request = FormRequest(login_post_url, formdata=login_form_data, callback=self.parse_main)
        yield request

    def parse_main(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        categories = hxs.select("//div[@id='catrootmenu']//a/@href").extract()
        for category in categories:
            url = urljoin_rfc(base_url, category)
            yield Request(url, callback=self.parse_main)

        items_table = hxs.select("//table[contains(@class, 'products-table')]")
        rows = items_table.select("tr")
        i = 0
        count = 0
        rows_count = len(rows)
        logging.error("Found rows: %d" % rows_count)
        while i < rows_count:
            image_row = rows.pop(0)
            name_row = rows.pop(0)
            sku_row = rows.pop(0)
            price_row = rows.pop(0)
            for name_cell, price_cell in zip(name_row.select('td'), price_row.select('td')):
                name = name_cell.select("a/text()").extract()
                if not name:
                    continue
                name = name[0]
                url = name_cell.select("a/@href").extract()
                if not url:
                    continue
                url = url[0]
                url = urljoin_rfc(base_url, url)
                price = price_cell.select(".//span[@class='product-price-value']/span/text()").extract()
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
                count +=1
            i += 4
        logging.error("Used rows: %d" % i)
