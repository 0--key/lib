from urlparse import urlparse, parse_qs
from urllib import urlencode
import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc


from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class WasserstromSpider(BaseSpider):
    name = 'wasserstrom.com'
    allowed_domains = ['wasserstrom.com']
    start_urls = ('http://www.wasserstrom.com/',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        #categories
        '''
        cats = hxs.select('//a[@class="category"]/@href').extract()
        '''
        cats = ['http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Winco_List_True_BrandDisplayView_1013200',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Thunder+Group_List_True_BrandDisplayView_204192',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Cardinal+International_List_True_BrandDisplayView_202571',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Libbey_List_True_BrandDisplayView_204083',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Victory+Refrigeration_List_True_BrandDisplayView_1013144',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Vollrath_List_True_BrandDisplayView_161583',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Dexter+Russell+Cutlery_List_True_BrandDisplayView_1012082',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Friedr.+Dick_List_True_BrandDisplayView_203090',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Cecilware+Corp_List_True_BrandDisplayView_1011943',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Turbo+Air_List_True_BrandDisplayView_1013106',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Eastern+Tabletop_List_True_BrandDisplayView_203074',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_G.E.T.+Enterprises_List_True_BrandDisplayView_181599',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_EMI+Yoshi+Inc._List_True_BrandDisplayView_1012141',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Beverage-Air_List_True_BrandDisplayView_1011848',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Amana_List_True_BrandDisplayView_1011732',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Chefwear_List_True_BrandDisplayView_1011960',
                'http://www.wasserstrom.com/restaurant-supplies-equipment/Brand_Bakers+Pride+Oven_List_True_BrandDisplayView_202560']

        for cat in cats:
            yield Request(cat, cookies={}, meta={'dont_merge_cookies': True})

        #pagination
        '''
        has_next = hxs.select('//form[@name="frmPagination"]//a[contains(text(), "Next")]')
        if has_next:
            total_results = hxs.select('//input[@name="totalResults"]/@value').extract()[0]
            url_data = urlparse(response.url)
            params = parse_qs(url_data.query)
            current_page = int(params.get('currPgNum', ['1'])[0])
            query = {'currPgNum': current_page + 1,
                     'pageSize': '20',
                     'pgStyle': 'Grid',
                     'results': '20',
                     'results2': '20',
                     'sortType': 'relevance',
                     'totalResults': total_results}

            yield response.url.split('?')[0] + '?' + urlencode(query)
        '''
        next = hxs.select('//ul[@class="results-pages"]//li/a[contains(text(), "Next")]/@href').extract()
        if next:
            args = re.search('\((.*)\)', next[0]).groups()[0].split(',')
            page_number = int(args[0].strip())
            page_size = 20
            total = args[3].strip()
            data = {'beginIndex': page_number * page_size,
                    'totalNoOfResult': total,
                    'stdPageSize': page_size,
                    'currPgNum': page_number,
                    'pgStyle': 'List',
                    'sort_results': 'relevance'}

            yield FormRequest.from_response(response, formname='goToPageForm', formdata=data,
                                            cookies={}, meta={'dont_merge_cookies': True})

        products = hxs.select('//ul[@class="product_types"]//a/@href').extract()
        products += hxs.select('//td[@class="searchproductdescription"]//a/@href').extract()
        for product in products:
            yield Request(product, callback=self.parse_product, cookies={}, meta={'dont_merge_cookies': True})

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        loader = ProductLoader(response=response, item=Product())
        loader.add_xpath('name', '//h1[@id="partNameId"]/text()')
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//font[@class="txt-purchaseprice20blue"]/text()')
        sku = ''.join(hxs.select('//b[contains(text(), "Model #:")]/../text()').extract()).strip()
        loader.add_value('sku', sku)

        yield loader.load_item()
