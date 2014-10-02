import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class arondia_spider(BaseSpider):
    name = 'arondia.com'
    allowed_domains = ['arondia.com', 'www.arondia.com']
    start_urls = ('http://www.arondia.com',)

    def parse_product(self, response):
        
        hxs = HtmlXPathSelector(response)
        pages = hxs.select('//select[@name="nbPagesPerPage"]')
        cat_text = hxs.select('//h2[@class="titre_image titre_image_niv1"]')
        if not pages and not cat_text:
            products = hxs.select('//div[@class="bloc_cadre_pied"]/form[@class="mini_fiche_ligne"]')
            for p in products:
                res = {}
                name = p.select('.//div[@class="colonne_1"]/div[@class="ligne_titre"]/span[@class="titre_descriptif"]/strong/text()')[0].extract().strip()
                url = response.url
                price = "".join(p.select('.//div[@class="lignebeige"]/div[@class="wrapperPrix"]/div/div/div/b/text()').re(r'([0-9\,\. ]+)')).strip()

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
        category_urls = hxs.select('//div[@id="menu_produit"]/ul/li/a/@href').extract()
        for url in category_urls:
            yield Request(urljoin_rfc(base_url,url))            
            
        #subcategories
        subcategory_urls = hxs.select('//ul[@id="famille_liste_es"]/li/a/@href').extract()
        for suburl in subcategory_urls:
            yield Request(urljoin_rfc(base_url,suburl))     
            
        #subsubcats
        subsubcat_urls = hxs.select('//div[@class="bloc_cadre bloc_modele2"]/div/div/form/div/div[@class="ligne_titre"]/a/@href').extract()
        for subsuburl in subsubcat_urls:
            yield Request(urljoin_rfc(base_url,subsuburl))             
        
        #next page
        next_pages = hxs.select('//form[@id="formPageHaut"]/a/@href').extract()
        if next_pages:
            for page in next_pages:
                yield Request(urljoin_rfc(base_url,page))

        # products
        for p in self.parse_product(response):
            yield p
