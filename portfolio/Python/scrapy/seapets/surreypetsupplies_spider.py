from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class SurreyPetSupplies(BaseSpider):
    name = "surreypetsupplies.co.uk"
    allowed_domains = ["surreypetsupplies.co.uk"]
    start_urls = ("http://www.surreypetsupplies.co.uk/sitemap.php",)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        cat_urls = hxs.select('//ul[@id="Sitemap_Categories"]//a[following-sibling::*[1][self::ul[@class="sitemap_products"]]]/@href').extract()

        for cat_url in cat_urls:
            yield Request(self._get_products_url(response, cat_url), callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)

        nextPageLink = hxs.select('//div[@id="center-main"]//a[@class="right-arrow"]/@href')
        if nextPageLink:
            yield Request(self._get_products_url(response, nextPageLink[0].extract()), callback=self.parse_products)

        products = hxs.select('//div[@id="center-main"]//div[@class="details"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)

            loader.add_xpath("name", 'a/text()')
            loader.add_xpath("sku", 'div[@class="sku"]/span/text()')

            # few prices were under div class desc
            price_selector = product.select('.//div[@class="price-row"]/span[@class="price-value"]/span/text()')
            if price_selector:
                price = price_selector[0].extract()
            else:
                price = "0.0"

            loader.add_value("price", price)

            relative_url = product.select('a/@href')[0].extract()
            loader.add_value("url", urljoin_rfc(get_base_url(response), relative_url))

            yield loader.load_item()

    def _get_products_url(self, response, relative_url):
        base_url = get_base_url(response)
        max_product_per_page = 50
        url = urljoin_rfc(base_url, relative_url + "?objects_per_page=%d" % max_product_per_page)
        return url
