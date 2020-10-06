import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy import log

from productloader import load_product
from scrapy.http import FormRequest

class siapets_spider(BaseSpider):
    name = 'petplanet.co.uk'
    allowed_domains = ['petplanet.co.uk', 'www.petplanet.co.uk']
    start_urls = ('http://www.petplanet.co.uk/dept.asp?dept_id=1',
                  'http://www.petplanet.co.uk/dept.asp?dept_id=2',
                  'http://www.petplanet.co.uk/dept.asp?dept_id=190',
                  'http://www.petplanet.co.uk/dept.asp?dept_id=3',
                  'http://www.petplanet.co.uk/dept.asp?dept_id=381',
                  'http://www.petplanet.co.uk/dept.asp?dept_id=382',
                  'http://www.petplanet.co.uk/dept.asp?dept_id=937',
                  'http://www.petplanet.co.uk/dept.asp?dept_id=624',
                  'http://www.petplanet.co.uk/dept.asp?dept_id=383',
                  'http://www.petplanet.co.uk/category.asp?dept_id=165',
                  'http://www.petplanet.co.uk/category.asp?dept_id=10',
                  'http://www.petplanet.co.uk/dept.asp?dept_id=3345',
                  'http://www.petplanet.co.uk/dept.asp?dept_id=1246',
                  'http://www.petplanet.co.uk/dept.asp?dept_id=485',
                  'http://www.petplanet.co.uk/dept.asp?dept_id=3353',
                  'http://www.petplanet.co.uk/category.asp?dept_id=3993'
                  )

    def parse_product(self, response):
        base_url = get_base_url(response)
        if re.search('product_group\.asp\?dept_id\=', str(response.url)):
            hxs = HtmlXPathSelector(response)
            products = hxs.select('//form[@action="xt_orderform_additem.asp?"]')
            for p in products:
                res = {}
                name = p.select('./p/a/@title').extract()
                if name:
                    url = p.select('./p/a/@href')[0].extract()
                    price = p.select('./p/span[@class="price"]/text()').re(r'([0-9][0-9\,\.]+)')
                    if not price:
                        price = p.select('./p/span[@class="price"][2]/text()').re(r'([0-9][0-9\,\.]+)')
                    res['url'] = urljoin_rfc(base_url,url)
                    res['description'] = name[0]
                    res['price'] = price[0].strip()
                    yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//td[@width="33.3%"]/table/tr/td/table/tr/td/a[1]/@href').extract()
        for url in category_urls:
            yield Request(urljoin_rfc(base_url,url))            
        
        #log.msg(str(response.url), level=log.WARNING)  
        if re.search('category\.asp\?dept_id\=', str(response.url)):
            
            groups_urls = hxs.select('//a[contains(@href,"product_group.asp?dept_id=")]/@href').extract()
            for group in groups_urls:
                yield Request(urljoin_rfc(base_url,group))
                
            prod_urls = hxs.select('//a[contains(@href,"product.asp?dept_id=")]/@href').extract()
            for prod in prod_urls:
                yield Request(urljoin_rfc(base_url,prod))                
                
            groups_urls = hxs.select('//form[contains(@action,"product_group.asp?dept_id=")]/@action').extract()
            for group in groups_urls:
                yield Request(urljoin_rfc(base_url,group))
                
            prod_urls = hxs.select('//form[contains(@action,"product.asp?dept_id=")]/@action').extract()
            for prod in prod_urls:
                yield Request(urljoin_rfc(base_url,prod))          
                
            prod_urls = hxs.select('//form[contains(@action,"xt_orderform_additem.asp?")]/p/a/@href').extract()
            for prod in prod_urls:
                yield Request(urljoin_rfc(base_url,prod))                     
       
        
        #add product
        if re.search('product\.asp\?dept_id\=', str(response.url)):
            res = {}
            name = hxs.select('//table/tr/td[1]/h1/text()').extract()[0]
            price = hxs.select('//table/tr/td[2]/h1/text()').re('[0-9\. \,]+')[0]
            url = response.url

            res['url'] = url
            res['description'] = name
            res['price'] = price
            yield load_product(res, response)
            
        
        #pages 
        pages = hxs.select('//td[@class="ps_scrollnav"]/a/@href').extract()
        for page in pages:
            yield Request(urljoin_rfc(base_url,page))  
            
        # products
        for p in self.parse_product(response):
            yield p
