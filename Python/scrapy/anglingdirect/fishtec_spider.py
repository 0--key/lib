import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class fishtec_spider(BaseSpider):
    name = 'fishtec.co.uk'
    allowed_domains = ['fishtec.co.uk', 'www.fishtec.co.uk']
    start_urls = ('http://www.fishtec.co.uk/Index-Fishtec-Fly-Fishing.cfm',
                  'http://www.fishtec.co.uk/Index-Fishtec-Carp-Fishing.cfm',
                  'http://www.fishtec.co.uk/Index-Fishtec-Match-Fishing.cfm',
                  'http://www.fishtec.co.uk/Index-Fishtec-Spinning-Fishing.cfm',
                  'http://www.fishtec.co.uk/Index-Fishtec-Sea-Fishing.cfm',
                  
                  )

    def parse_product(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        res = {}
        options = hxs.select("//select[@name='SKURecNum']/option/text()").extract()
        if options:
            #options
            name = hxs.select("//div[@class='buybox']/table/tr/td/h1/text()").extract()
            if not name:
                name = hxs.select("//h1[@class='productNameDN']/text()").extract()
            url = response.url
            for option in options:
                try:
                    name2 = re.match(r'(.*) -.*',option.strip()).group(1)
                except:
                    continue
                try:
                    price = re.match(r'.*\xa3(.*)',option.replace("\r","").replace("\n","").strip()).group(1)
                except:
                    price = None
                if not price:
                    price = "".join(hxs.select("//p[@class='ProductDetailPrice']/a/font[@class='BodyMain']/text()").re(r'\xa3([0-9\,\. ]+)')).strip()
                    if not price:
                        price = "".join(hxs.select('//p[@class="ProductDetailPrice"]/font[1]/b/text()').re(r'\xa3([0-9\,\. ]+)')).strip()
                res['url'] = urljoin_rfc(base_url,url)
                res['description'] = name[0].strip() + u' ' + name2
                res['price'] = price
                yield load_product(res, response)
        else:
            name = hxs.select("//div[@class='buybox']/table/tr/td/h1/text()").extract()
            if not name:
                name = hxs.select("//h1[@class='productNameDN']/text()").extract()
                if not name:
                    name = hxs.select("//div[@class='buybox']/table/tr/td/table/tr/td/h1/text()").extract()
            url = response.url
            price = "".join(hxs.select("//p[@class='ProductDetailPrice']/strong/a/font[@class='BodyMain']/text()").re(r'\xa3([0-9\,\. ]+)')).strip()
            if not price: 
                price = "".join(hxs.select("//p[@class='ProductDetailPrice']/a/font[@class='BodyMain']/text()").re(r'\xa3([0-9\,\. ]+)')).strip()
                if not price:
                    price = "".join(hxs.select('//p[@class="ProductDetailPrice"]/strong/font/b/text()').re(r'\xa3([0-9\,\. ]+)')).strip()
                    if not price: 
                        price = "".join(hxs.select('//p[@class="ProductDetailPrice"]/font/b/text()').re(r'\xa3([0-9\,\. ]+)')).strip()
            res['url'] = urljoin_rfc(base_url,url)
            res['description'] = name[0].strip()
            res['price'] = price
            yield load_product(res, response)
        
        


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//span[@class="submenu"]/a/@href').extract()
        for url in category_urls:
            yield Request(url + '?showall=View%20All')
            
        #additional categories
        hxs = HtmlXPathSelector(response)
        acategory_urls = hxs.select('//div[@id="masterdiv"]/h3/a/@href').extract()
        for aurl in acategory_urls:
            yield Request(aurl + '?showall=View%20All')
        
        #products
        products = hxs.select('//div[@class="counterbox"]')
        for p in products:
            url_product = p.select('.//td[@class="ProductName"]/a/@href')[0].extract()
            yield Request(url_product, callback=self.parse_product)