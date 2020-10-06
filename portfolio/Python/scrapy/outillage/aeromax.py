# scrapy includes
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

# spider includes
from product_spiders.items import Product, ProductLoader

# main class
class AeromaxSpider(BaseSpider):

    # setup
    name = "aeromax-pistoletpeinture.com" # Name must match the domain
    allowed_domains = ["aeromax-pistoletpeinture.com"]
    start_urls = ["http://www.aeromax-pistoletpeinture.com",]

    # main request
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # get subcategories
        cat1urls = hxs.select("//ul[starts-with(@class, 'mnDeroul ')]//a/@href").extract()

        # iterate subcategories
        for cat1url in cat1urls:
            yield Request(urljoin_rfc(base_url, cat1url))

        cat2urls = hxs.select("//div[@class='PaginationHaut']//div[@class='familleArticl_tit']/a/@href").extract()
        for cat2url in cat2urls:
            yield Request(urljoin_rfc(base_url, cat2url))

        # crawl next page
        onglet = hxs.select("//div[@class='PaginationHaut']//table[@class='Onglet']//td[@class='Onglet']")
        if onglet:
            # it always contains two and the "next" is always the second one
            nextpage = onglet[1].select("./a/@href")

            # if there is a next page...
            if nextpage:
                yield Request(urljoin_rfc(base_url, nextpage[0].extract()))

        # iterate products
        for product in self.parse_products(hxs, base_url):
            yield product

    # gather products
    def parse_products(self, hxs, base_url):
        products = hxs.select("//div[@class='BoiteDegrad']").select(".//div[@class='ListArticl_elmt_Bck']")

        for product in products:
            product_loader = ProductLoader(Product(), product)

            # extract values
            urlAndNameNode = product.select(".//div[@class='ListArticl_tit']/a")
            name = urlAndNameNode.select('text()').extract()[0]
            url = urlAndNameNode.select("@href").extract()[0]
            price = ' '.join(product.select('.//div[@class="ListArticl_prx"]//text()').extract())

            # add values
            product_loader.add_value('name', name)
            product_loader.add_value('url', urljoin_rfc(base_url, url))
            product_loader.add_value('price', price)

            yield product_loader.load_item()
