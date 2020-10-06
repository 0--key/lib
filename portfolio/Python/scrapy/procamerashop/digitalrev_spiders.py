import os
import re
import csv
import string
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url
from product_spiders.fuzzywuzzy import process

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class DigitalrevSpider(BaseSpider):
    name = 'digitalrev.com'
    allowed_domains = ['digitalrev.com']

    def start_requests(self):
        yield FormRequest('http://www.digitalrev.com/country/changeCountry.dr', 
                                   method='POST',
                                   formdata={'countryId':'1'}, 
                                   callback=self.parse_country)

    def parse_country(self, response):
        yield Request('http://www.digitalrev.com/search?t=pro&q=')

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = map(self._get_category_id, hxs.select('//li[@class="select_right_div_li"]/@onclick').extract())
        for category in categories:
            url = 'http://www.digitalrev.com/shop/category/showProductList.dr?categoryId=%s'
            yield Request(url % category, callback=self.parse_category, meta={'category':category})
            
    def parse_category(self, response):
        hxs = HtmlXPathSelector(response)
        pages = (int(hxs.select('//*[@id="recordCount"]/text()').extract()[0].strip().split(' ')[-1])/40)
        if pages:
            for page in range(1, pages+2):
                
 
                yield FormRequest('http://www.digitalrev.com/shop/category/showProductList.dr', 
                                   method='POST',
                                   formdata={'categoryId':response.meta['category'],
                                             'col':'Best_Reselers',
                                             'page.pageSize':'40',
                                             'page.currentPage':'%s' % page,
                                             'showtype':'1'}, 
                                   dont_filter=True,
                                   callback=self.parse_products,
                                   meta={'page':page})
        else:
            yield FormRequest('http://www.digitalrev.com/shop/category/showProductList.dr', 
                                   method='POST',
                                   formdata={'categoryId':response.meta['category'],
                                             'col':'Best_Reselers',
                                             'page.pageSize':'20',
                                             'page.currentPage':'1',
                                             'showtype':'1'}, 
                                   dont_filter=True, 
                                   callback=self.parse_products,
                                   meta={'page':1})

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@id="cp_list01"]/div[@class="cp"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'div/a/@title')
            relative_url = ''.join(product.select('div/a/@href').extract())
            loader.add_value('url', urljoin_rfc(get_base_url(response), relative_url))
            price = product.select('div[@class="cate_pro_priceDiv"]/text()').extract()
            if price:
                #Find price.
                re_price = re.findall(r"[-+]?\d*\.\d+|\d+", price[0].replace(',',''))
                if re_price:
                    #Format price with two decimals
                    num = str(float(re_price[0])).split('.')
                    price = ''.join((num[0],'.', num[1][:2]))
                else:
                    price = 0.0
            else:
                price = 0.0
            loader.add_value('price', price)
            yield loader.load_item()

    def _get_category_id(self, data):                                                               
        return string.split(string.split(data,'(')[-1],')')[0]
