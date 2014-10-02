# scrapy includes
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

# spider includes
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

# main class
class PainRelieverSpider(BaseSpider):

    # setup
    name = "painreliever.com"
    allowed_domains = ["painreliever.com"]
    # start_urls = ["http://www.painreliever.com",]
    start_urls = ["http://www.painreliever.com/sitemap.html",]

    # main request
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # cat1urls = hxs.select('//div[@class="main_leftbar_div"]//div[@class="tier1"]//a/@href').extract()

        cat1urls = hxs.select("//div[@id='main_content_div']/table")[0].select("//a/@href").extract()

        # get categories and iterate them
        # cat1urls = hxs.select('//h3/following-sibling::table//a/@href').extract()

        for cat1url in cat1urls:
            yield Request(urljoin_rfc(base_url, cat1url), callback=self.parse_categories)

    def parse_categories(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # get subcategories and iterate them
        catNUrls = set(hxs.select('//ul[@id="cat_subcat_container"]//a/@href').extract())

        for catNUrl in catNUrls:
            yield Request(urljoin_rfc(base_url, catNUrl), callback=self.parse_categories)

        # crawl next page
        nextPageLink = hxs.select("//a[contains(text(), 'Next >')]/@href")
        if nextPageLink:
            yield Request(urljoin_rfc(base_url, nextPageLink[0].extract()), callback=self.parse_categories)

            # iterate products
        productUrls = hxs.select('//li[@class="product_cat_control"]/a/@href').extract()
        for productUrl in productUrls:
            yield Request(urljoin_rfc(base_url, productUrl), callback=self.parse_product)

    # gather products
    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        productIsNotAvailable = hxs.select("//span[contains(text(), 'Sorry, this Item is No Longer Available')]")

        if not productIsNotAvailable:
            loader = ProductLoader(response=response, item=Product())
            loader.add_xpath('name', '//h1[@id="product_header"]/text()')
            loader.add_value('url', response.url)
            loader.add_xpath('price', '//span[@id="our_price"]/text()')

            r = hxs.select("//div[@id='product_image_container']/../../text()").extract()
            r = [x.strip() for x in r if x.strip()]
            sku = r[0].replace('Model: ', '')

            loader.add_value('sku', sku)

            yield loader.load_item()