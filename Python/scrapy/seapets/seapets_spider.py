import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class siapets_spider(BaseSpider):
    name = 'seapets.co.uk'
    allowed_domains = ['seapets.co.uk', 'www.seapets.co.uk']
    start_urls = ('http://www.seapets.co.uk',)

    def parse_product(self, response):
        base_url = get_base_url(response)
        if re.search('all-products\.html$', str(response.url)):
            hxs = HtmlXPathSelector(response)
            products = hxs.select('//div[@id="double-column-wrapper"]/div[@id="col-2"]/div[@class="col-2-text-div"]/div[@class="col-2-divider"]')
            for p in products:
                if p.select(".//img[@class='add-to-basket']").extract():
                    res = {}
                    name = p.select('.//h2[@class="subcategory-h2"]/a/text()')[0].extract()
                    if name:
                      url = p.select('.//h2[@class="subcategory-h2"]/a/@href')[0].extract()
                      price = p.select('.//div[@class="product-list-right"]/div[@class="product-list-price-etc"]/div/p[@class="the-price"]/text()').re(r'([0-9\,\. ]+)')[0].strip()

                      res['url'] = urljoin_rfc(base_url,url)
                      res['description'] = name
                      res['price'] = price
                      yield load_product(res, response)
                else:
                    suburl = p.select('.//h2[@class="subcategory-h2"]/a/@href')[0].extract()
                    yield Request(urljoin_rfc(base_url,suburl))


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//div[@id="category-menu"]/ul/li/a/@href').extract()
        for url in category_urls:
            yield Request(urljoin_rfc(base_url,url))            
            
        #subcategories
        subcategory_urls = hxs.select('//div[@id="double-column-wrapper"]/div[@id="col-2"]/div[@class="col-2-text-div"]/div[@class="col-2-divider"]/div[@class="category-right"]/a/@href').extract()
        for suburl in subcategory_urls:
            yield Request(urljoin_rfc(base_url,suburl))     

        
        #detailed products
        counter = 0
        products = hxs.select('//div[@class="product-right"]/form/table/tr')
        for p in products:
            counter = counter + 1
            if p.select("./td[@style='font-size: 12px;']").extract(): 
                res = {}
                name = p.select('./td[@style="font-size: 12px;"]/a/text()')[0].extract()
                url = p.select('./td[@style="font-size: 12px;"]/a/@href')[0].extract()
                price = products[counter].select('./td[1]/span[@class="the-price"]/text()').re(r'([0-9\,\. ]+)')[0].strip()

                res['url'] = urljoin_rfc(base_url,url)
                res['description'] = name
                res['price'] = price
                yield load_product(res, response)
        
        
        
        
        # products
        for p in self.parse_product(response):
            yield p
