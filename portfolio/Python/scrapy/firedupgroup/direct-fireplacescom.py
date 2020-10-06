from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class DirectFireplacesComSpider(BaseSpider):
    name = 'direct-fireplaces.com'
    allowed_domains = ['direct-fireplaces.com']
    start_urls = ('http://www.direct-fireplaces.com/',)

    def parse(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//ul[@class="category-list list-vertical"]/li/a/@href').extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        # subcategories
        hxs = HtmlXPathSelector(response)
        subcategory_urls = hxs.select('//table[@class="sub-categories"]/tr/td/a/@href').extract()
        for url in subcategory_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        # pages
        page_urls = hxs.select("//div[@class='DataViewPager']/center/ul/li/a/@href").extract()
        for url in page_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        # products list
        products = hxs.select("//div[@class='DataViewCell']/table")
        if not products:
            print "ERROR!! NO PRODUCTS!! %s " % response.url
        for product_el in products:
            name = product_el.select('.//div[@class="DataViewItemProductTitle"]/a/text()').extract()
            if not name:
                print "ERROR!! NO NAME!! %s" % response.url
                continue

            url = product_el.select('.//div[@class="DataViewItemProductTitle"]/a/@href').extract()
            if not url:
                print "ERROR!! NO URL!! %s" % response.url
                continue
            url = url[0]

            price = product_el.select('.//div[@class="DataViewItemOurPrice"]/text()').extract()
            if not price:
                print "ERROR!! NO PRICE!! %s" % response.url
                price = '0'
            else:
                price = price[0]

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()
