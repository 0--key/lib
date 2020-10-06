# scrapy includes
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

# spider includes
from product_spiders.items import Product, ProductLoader

# main class
class MedLiefSpider(BaseSpider):

    # setup
    name = "medlief.com" # Name must match the domain
    allowed_domains = ["medlief.com"]
    # start_urls = ["http://www.medlief.com/sitemap.html",]
    start_urls = ["http://www.medlief.com/products-by-category.html",]

    # main request
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        #categoryUrls = hxs.select("//a[text()='Category']/../div/ul/li/a/@href").extract()
        #categoryUrls = hxs.select("//a[text()='Category']/../div/ul//a/@href").extract()

        # categoryUrls = hxs.select('//div[@class="divContainer"]//ul[@class="left-menu"]//ul[@class="sf-vertical sf-menu sf-js-enabled sf-shadow"]//a/@href').extract()
        # categoryUrls = hxs.select('//div[@class="content_l"]//li/a/@href').extract()
        categoryUrls = hxs.select('//div[@class="content_l"]/div/ul[@class="left-menu"]/li/ul//a/@href').extract()

        for categoryUrl in categoryUrls:
            yield Request(categoryUrl, callback=self.parse_categories)

    # enter categories
    def parse_categories(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        # proceed only it is a products page and not an upper level category
        hasSubCategories = hxs.select("//div[@class='listing-type-grid catalog-listing']")[0].select(".//a/@href")

        if hasSubCategories:
            subCatUrls = hasSubCategories.extract()

            for subCatUrl in subCatUrls:
                yield Request(subCatUrl, callback=self.parse_categories)

        else:
            # go to the next page
            nextPageLink = hxs.select("//img[@alt='Next Page']/../@href")
            nextPageLink2 = hxs.select("//a[text()='Next']/@href")

            # if there is a next page... (the link has different formats in different pages)
            if nextPageLink:
                link = nextPageLink.extract()[0]
                yield Request(urljoin_rfc(base_url, link), callback=self.parse_categories)

            elif nextPageLink2:
                link = nextPageLink2.extract()[0]
                yield Request(urljoin_rfc(base_url, link), callback=self.parse_categories)

            productUrls = hxs.select("//li[@class='item']/div[@class='product-image']/a/@href").extract()

            for productUrl in productUrls:
                yield Request(urljoin_rfc(base_url, productUrl), callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        prices = hxs.select('//span[@class="price"]/text()')
        loader = ProductLoader(response=response, item=Product())

        if prices:
            loader.add_value('price', prices[len(prices) - 1])

        loader.add_xpath('name', '//div[@class="product_l"]/h2/text()')
        loader.add_value('url', response.url)

        txt = hxs.select("//label[starts-with(text(), 'Manufacturers')]").extract()[0]
        sku = txt[txt.find('/label>')+7:]
        loader.add_value('sku', sku.strip())

        yield loader.load_item()