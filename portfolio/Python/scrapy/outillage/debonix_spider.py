import re
import json
import urllib


from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy import log

from productloader import load_product
from scrapy.http import FormRequest
from string import join

class debonix_spider(BaseSpider):
    name = 'debonix.fr'
    inserted_products = set([])
    allowed_domains = ['debonix.fr', 'www.debonix.fr']
    start_urls = ('http://www.debonix.fr/outillage-electroportatif.html',
                  'http://www.debonix.fr/mesures-controles.html',
                  'http://www.debonix.fr/outillage-a-main.html',
                  'http://www.debonix.fr/accessoires.html',
                  'http://www.debonix.fr/consommables.html',
                  'http://www.debonix.fr/protection-individuelle.html',
                  'http://www.debonix.fr/gros-oeuvre-manutention.html',
                  'http://www.debonix.fr/jardins-forets.html',)

    def parse_product(self, response):
        
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//ol[@class="category list"]/li')
        for p in products:
            res = {}
            name = join(p.select('.//div/div/h2//a[1]/text()').extract())
            url = join(p.select('.//div/div/h2/a[1]/@href').extract())
            if name+url in self.inserted_products:
                continue
            """price = p.select('.//div/div/div[@class="prix"]/span[@class="price-including-tax"]/span[@class="price"]/text()').re(r'([0-9\,\. ]+)')
            if not price:
              price = p.select('.//div/div/div[@class="prix"]/ins/span[@class="price-including-tax"]/span[@class="price"]/text()').re(r'([0-9\,\. ]+)')
            if len(price) > 1:
              price_ = str(price[0]) + str(price[1])
            else:
              price_ = price[0]"""
			
            price_url = join(p.select('.//div/div/div[@class="prix"]/span[@class="price-including-tax"]/span[1]/img/@src').extract())
            if not price_url:
                price_url = join(p.select('.//div/div/div[@class="prix"]/ins/span[@class="price-including-tax"]/span[1]/img/@src').extract())

            if price_url:
                params = urllib.urlencode({'url': price_url, 'resize': '200', 'mode': '8', 'blur':'1', 'format':'float'})
                f = urllib.urlopen("http://178.63.95.196/ocr/get_price_from_image?%s" % params)
                jdata = json.loads(f.read())
                log.msg(str(jdata), log.DEBUG)
                price = jdata['price'].encode('utf-8')
                price = price.replace(" ","").replace(",",".")
                log.msg(str(price),log.DEBUG)
            else:
                price = ""

            res['url'] = url
            res['description'] = name
            res['price'] = price
            self.inserted_products.add(name+url)
            yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
            
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//div[@class="category"]/ol/li/a/@href').extract()
        for url in category_urls:
            yield Request(url)            
            
            
        #next page
        next_pages = hxs.select('//div[@class="pager"][1]/ol/li[@class="number"]/a/@href').extract()
        if next_pages:
            for page in next_pages:
                yield Request(page)

        # products
        for p in self.parse_product(response):
            yield p
