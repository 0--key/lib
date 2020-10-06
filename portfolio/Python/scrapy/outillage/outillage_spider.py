import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class Outillage_spider(BaseSpider):
    name = 'outillage-online.fr'
    allowed_domains = ['outillage-online.fr', 'www.outillage-online.fr']
    start_urls = ('http://www.outillage-online.fr/marques',
    'http://www.outillage-online.fr/accessoires-et-consommables',)
    start_urls = ('http://www.outillage-online.fr/marques',
                  'http://www.outillage-online.fr/outillage-a-main',
                  'http://www.outillage-online.fr/mobilier-atelier-et-rangement',
                  'http://www.outillage-online.fr/outillage-electroportatif',
                  'http://www.outillage-online.fr/outillage-stationnaire',
                  'http://www.outillage-online.fr/nettoyage-et-entretien-1',
                  'http://www.outillage-online.fr/levage-et-manutention',
                  'http://www.outillage-online.fr/protection-individuelle',
                  'http://www.outillage-online.fr/exterieurs-et-jardin',
                  'http://www.outillage-online.fr/peinture-et-revetements-des-murs',
                  'http://www.outillage-online.fr/outillage-metier-et-projet',
    )

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//li[@class="item last"]')
        if products:
            for p in products:
                res = {}
                name = p.select('.//h2[@class="product-name"]/a/text()')[0].extract().strip()
                url = p.select('.//h2[@class="product-name"]/a/@href')[0].extract().strip()
                price = "".join(p.select('.//div[@class="price-box"]/span[@class="regular-price"]/span[@class="price"]/text()').re(r'([0-9\,\. ]+)')).strip()
                if not price:
                    price = "".join(p.select('.//div[@class="price-box"]/p[@class="special-price"]/span[@class="price"]/text()').re(r'([0-9\,\. ]+)')).strip()
                res['url'] = url
                res['description'] = name
                res['price'] = price
                yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//ul[@class="bare-list"]/li/a/@href').extract()
        for url in category_urls:
            yield Request(url)
            
        #categories2
        hxs = HtmlXPathSelector(response)
        category2_urls = hxs.select('//div[@class="block-content"]/ul[@class="level-2"]/li/a/@href').extract()
        for url2 in category2_urls:
            yield Request(url2)            

        #next page
        next_pages = hxs.select('//a[@class="next i-next"]/@href').extract()
        if next_pages:
            for page in next_pages:
                yield Request(urljoin_rfc(base_url,page))

        # products
        for p in self.parse_product(response):
            yield p
