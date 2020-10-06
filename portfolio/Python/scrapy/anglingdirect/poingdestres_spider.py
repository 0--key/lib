import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class climaxtackle_spider(BaseSpider):
    name = 'poingdestres.co.uk'
    allowed_domains = ['poingdestres.co.uk', 'www.poingdestres.co.uk']
    start_urls = ('http://www.poingdestres.co.uk',)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        res = {}
        options = hxs.select("//div[@id='optionscontainer']/div[@class='variants']/select/option/text()").extract()
        if options:
            #options
            name = hxs.select("//div[@class='ProductDetails']/h1/text()")[0].extract().strip()
            url = response.url
            for option in options:
                name2 = re.match(r'(.*) -',option).group(1)
                price = re.match(r'.*\xa3(.*)',option).group(1)
                res['url'] = url
                res['description'] = name + u' ' + name2
                res['price'] = price
                yield load_product(res, response)
        else:
            name = hxs.select("//div[@class='ProductDetails']/h1/text()")[0].extract().strip()
            url = response.url            
            price = "".join(hxs.select("//div[@id='unitprice']/span/text()").re(r'([0-9\,\. ]+)')).strip()
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
        categories_urls = hxs.select('//div[@id="navigation"]/div/h2/a/@href').extract()
        for url in categories_urls:
            yield Request(url)
            
        #subcats
        subcats_urls = hxs.select('//div[@id="navigation"]/div/div/a/@href').extract()
        for surl in subcats_urls:
            yield Request(surl)        
            
        #pages
        pages_urls = hxs.select('//span[@id="Pagination"]/a/@href').extract()
        for page in pages_urls:
            yield Request(page)
            
        products = hxs.select('//div[@class="listitem"]')
        for p in products:
            url_product = p.select('.//div[@class="heading"]/a/@href')[0].extract()
            yield Request(urljoin_rfc(base_url,url_product), callback=self.parse_product)