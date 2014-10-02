from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class VeryCoUkSpider(BaseSpider):
    name = 'very.co.uk'
    allowed_domains = ['very.co.uk']
    start_urls = (
    'http://www.very.co.uk/electricals/heating-cooling/fires/e/b/4645/s/bestsellers,0.end',
    'http://www.very.co.uk/electricals/heating-cooling/wall-mounted-fires/e/b/4651/s/bestsellers,0.end',
    'http://www.very.co.uk/electricals/heating-cooling/fire-suites/e/b/12831/s/bestsellers,0.end'
    )

    def parse(self, response):
        URL_BASE = get_base_url(response)

        hxs = HtmlXPathSelector(response)

        pages_urls = hxs.select("//div[@class='pagination']/ol/li/a/@href").extract()
        for url in pages_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        products_els = hxs.select("//div[@class='product']")
        for product_el in products_els:
            name = product_el.select("div[@class='prodinfo']/div[@class='prodright']/h3/a/child::*/text()").extract()
            if not name:
                print 'ERROR!! NO NAME!! %s' % response.url
                continue
            name = " ".join(name)

            url = product_el.select("div[@class='prodinfo']/div[@class='prodright']/h3/a/@href").extract()
            if not url:
                print 'ERROR!! NO URL!! %s' % response.url
                continue
            url = url[0]
            url = urljoin_rfc(URL_BASE, url)

            price = product_el.select("div[@class='prodinfo']/div[@class='prodleft']/dl[@class='price']/dd/span[@class='now']/text()").extract()
            if not price:
                print 'ERROR!! NO PRICE!! %s' % response.url
                continue
            price = price[0]

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)

            loader.add_value('sku', '')

            yield loader.load_item()
