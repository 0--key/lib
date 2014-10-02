from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class FiresrusCoUkSpider(BaseSpider):
    name = 'firesrus.co.uk'
    allowed_domains = ['firesrus.co.uk']
    start_urls = (
        # all products page
        'http://www.firesrus.co.uk/catalog/quick_research.php?keywords=&search_in_description=1&pfrom=&pto=&categories_id=&inc_subcat=1&manufacturers_id=&x=37&y=5',
    )

    def parse(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # pages
        page_urls = hxs.select("//a[@class='pageResults']/@href").extract()
        for url in page_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        # products list
        products = hxs.select("//table[@class='productListing']/tr[contains(@class, 'productListing')]")
        if not products:
            print "ERROR!! NO PRODUCTS!! %s " % response.url
        for product_el in products:
            name = product_el.select('td[@class="productListing-data"][3]/a/text()').extract()
            if not name:
                print "ERROR!! NO NAME!! %s" % response.url
                continue

            url = product_el.select('td[@class="productListing-data"][3]/a/@href').extract()
            if not url:
                print "ERROR!! NO URL!! %s" % response.url
                continue
            url = url[0]

            price = product_el.select('td[@class="productListing-data"][4]/span[@class="productSpecialPrice"]/text()').extract()
            if not price:
                price = product_el.select('td[@class="productListing-data"][4]/text()').extract()
                if not price:
                    print "ERROR!! NO PRICE!! %s" % response.url
                    continue
            price = price[0]

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()
