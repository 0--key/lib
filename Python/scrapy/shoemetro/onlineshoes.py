from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request  #, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
import logging as log


class OnlineShoesSpider(BaseSpider):
    name = 'onlineshoes.com'
    allowed_domains = ['www.onlineshoes.com', 'onlineshoes.com']
    start_urls = ['http://onlineshoes.com']

    def parse(self, response):
        ''' This function parses main page and
        extracts [View All <Category Products>] links
        '''
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)
        categories = hxs.select("//p[@class='bold cta']/a/@href").extract()
            #"//ul[id='mainNavDropdowns']/li/a[@sitecat=''")
        for url in categories:
            log.critical("Yielding request for {}".format(url))
            yield Request(
                urljoin_rfc(base_url, url),
                callback=self.parse_category
            )

    def parse_category(self, response):
        log.critical("="*10)
        log.critical("PARS CATEGORY FUNC")
        log.critical("="*10)

        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)
        products = hxs.select((
            "//div[@id='products']/div[@class='productThumbSize200"
            " productThumbContainer']"
        ))
        for prod in products:
            loader = ProductLoader(response=response, item=Product())
            loader.add_value(
                'sku',
                "".join(prod.select("./a[@class='productThumb']/@title").extract()).split('-')[-1]
            )
            loader.add_value(
                'url',
                urljoin_rfc(base_url,
                "".join(prod.select("./a[@class='productThumb']/@href").extract())))
            loader.add_value('name',
                " ".join(prod.select(".//div[@class='productThumbTitle']//text()").extract())
            )
            two_p = prod.select(".//div[@id='productThumbPrice']/span[1]/text()").extract()
            loader.add_value(
                'price', (
                    two_p if two_p
                    else prod.select(
                        ".//div[@id='productThumbPrice']/text()").extract()
                )
            )
            yield loader.load_item()

        next_page = hxs.select(
            "//div[@id='paginationBottom']//a[@class='nextPage'][1]/@href"
        ).extract()
        if next_page:
            # test there's [Next Page] link exists on the page
            yield Request(next_page[0], self.parse_category)

