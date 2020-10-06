import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class guedo_outillage_spider(BaseSpider):
    name = 'guedo-outillage.fr'
    allowed_domains = ['guedo-outillage.fr', 'www.guedo-outillage.fr']
    start_urls = ('http://www.guedo-outillage.fr/perceuse-visseuse-2.htm',
                  'http://www.guedo-outillage.fr/perforateur-burineur-3.htm',
                  'http://www.guedo-outillage.fr/meuleuse-ponceuse-4.htm',
                  'http://www.guedo-outillage.fr/rabot-defonceuse-7.htm',
                  'http://www.guedo-outillage.fr/scie-portative-stationnaire-6.htm',
                  'http://www.guedo-outillage.fr/mesure-controle-11.htm',
                  'http://www.guedo-outillage.fr/foret-jardin-8.htm',
                  'http://www.guedo-outillage.fr/pack-machines-9.htm',
                  'http://www.guedo-outillage.fr/accessoire-consommable-10.htm'
                  )

    def parse_product(self, response):
        
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//table[@class="tableliste"]/tr[contains(@class,"resume_liste")]')
        cnt = 0
        for p in products:
            res = {}
            try:
	        name = p.select('.//td/h2/a/text()').re('(.*)\n.*')[0]
	    except:
	        continue

            price = p.select('.//td/div/div/strong').re('[0-9,\. ]+')
            if not price:
                price = p.select('.//td/div/div/div/strong').re('[0-9,\. ]+')
            res['url'] = p.select('.//td/h2/a/@href').extract()[0]
            res['description'] = name
            res['price'] = price[0]
            yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
            
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//div[@class="icones_sup"]/div[@class="icones_filles"]/div/div/a[1]/@href').extract()
        for url in category_urls:
            yield Request(url)            
            
        #subcategories
        subcategory_urls = hxs.select('//ul[@id="product_list"]/li/div/a/@href').extract()
        for url in subcategory_urls:
            yield Request(url)
        
        #pages
        pages_urls = hxs.select('//div[@class="pagination"]/table/tr/td/a/@href').extract()
        for url in pages_urls:
            yield Request(url)    
            
        #product
        product_ = hxs.select('//div[@id="fiche_produit"]/form')
        if product_:
            res = {}
            res['description'] = product_.select('.//h1/text()').extract()[0].strip()
            res['url'] = response.url
            price_ = product_.select('.//div[@class="ZonePrix"]/div[@class="prix"]/div/strong/text()').re('[0-9,\. ]+')
            if not price_:
	        price_ = product_.select('.//div[@class="ZonePrix"]/div[@class="prix"]/strong/text()').re('[0-9,\. ]+')
	    res['price'] = price_[0]
	    yield load_product(res, response)
            

        # products
        for p in self.parse_product(response):
            yield p