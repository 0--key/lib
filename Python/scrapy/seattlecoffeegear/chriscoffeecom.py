import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

PROXY = 'http://ec2-107-20-62-101.compute-1.amazonaws.com:6543'

def proxyRequest(*args, **kwargs):
    meta = {'proxy': PROXY}
    if 'meta' in kwargs:
        kwargs['meta'].update(meta)
    else:
        kwargs['meta'] = meta
    return Request(*args, **kwargs)


class ChriscoffeeComSpider(BaseSpider):
    name = 'chriscoffee.com'
    allowed_domains = ['chriscoffee.com']
    start_urls = (
        'http://www.chriscoffee.com/products/home',
        'http://www.chriscoffee.com/products/food',
        'http://www.chriscoffee.com/products/office',
        'http://www.chriscoffee.com/products/coffee'
        )
    download_delay = 2

    def parse(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # sub_category urls
        sub_category_urls = hxs.select("//a[@class='subsectiontitle']/@href").extract()
        for url in sub_category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield proxyRequest(url, callback=self.parse_subcategory)

    def parse_subcategory(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # product urls
        urls = hxs.select("//a[@class='subsectiontitle']/@href").extract()
        for url in urls:
            url = urljoin_rfc(URL_BASE, url)
            yield proxyRequest(url, callback=self.parse_product)


    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        product_el = hxs.select("/html/body/table/tr/td[2]/table[position()=last()-1]/tr/td[1]")
        name = product_el.select("p[@class='normale']/span[@class='emphasis']/text()").extract()
        if not name:
            print "ERROR!! NO NAME!! %s" % response.url
            logging.error("ERROR!! NO NAME!! %s" % response.url)
            return
        name = name[0]

        url = response.url

        items_title_pos, accessories_title_pos = None, None
        prices_table = product_el.select("table[last()]/form")
        for row in prices_table.select("tr"):
            col = row.select("td[@class='normalreverse']")
            if col:
                if col.select("strong[text()='Items']"):
                    items_title_pos = len(row.select("preceding-sibling::tr").extract()) + 1
                elif col.select("strong[text()='Suggested Accessories']"):
                    accessories_title_pos = len(row.select("preceding-sibling::tr").extract()) + 1
        if items_title_pos is not None:
            if accessories_title_pos is not None:
                sub_cond = " and position()<%d" % accessories_title_pos
            else:
                sub_cond = ""
            sub_items = prices_table.select("tr[position()>%d%s]" % (items_title_pos, sub_cond))
            for row in sub_items:
                sub_name = row.select("td[1]/text()").extract()
                if not sub_name:
                    print "ERROR!! NO NAME!! %s" % response.url
                    logging.error("ERROR!! NO NAME!! %s" % response.url)
                    continue
                sub_name = sub_name[0]
                price = row.select("td[3]/text()").extract()
                if not price:
                    print "ERROR!! NO PRICE!! %s" % response.url
                    logging.error("ERROR!! NO PRICE!! %s" % response.url)
                    continue
                price = price[0]

                product = Product()
                loader = ProductLoader(item=product, response=response)
                loader.add_value('url', url)
                loader.add_value('name', "%s - %s" % (name, sub_name))
                loader.add_value('price', price)
                loader.add_value('sku', '')
                yield loader.load_item()
