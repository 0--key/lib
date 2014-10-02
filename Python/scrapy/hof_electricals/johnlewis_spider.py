from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader


class JohnLewisSpider(BaseSpider):
    name = 'johnlewis.com-electricals'
    allowed_domains = ['johnlewis.com']
    start_urls = ["http://www.johnlewis.com/Electricals/Food+Processors_2c+Mixers+and+Blenders/Food+Processors_2c+Mixers+and+Blenders/Food+Processors+/545/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Food+Processors_2c+Mixers+and+Blenders/Food+Processors_2c+Mixers+and+Blenders/Food+Mixers/543/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Food+Processors_2c+Mixers+and+Blenders/Food+Processors_2c+Mixers+and+Blenders/Blenders/525/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Food+Processors_2c+Mixers+and+Blenders/Food+Processors_2c+Mixers+and+Blenders/Hand+Blenders/19939/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Food+Processors_2c+Mixers+and+Blenders/Food+Processors_2c+Mixers+and+Blenders/Choppers+and+Grinders/527/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Food+Processors_2c+Mixers+and+Blenders/Food+Processors_2c+Mixers+and+Blenders/Juicers+and+Presses/538/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Food+Processors_2c+Mixers+and+Blenders/Food+Processors_2c+Mixers+and+Blenders/Ice+Cream+Makers/537/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Coffee+Machines/Coffee+Machines/Coffee+Machines/529/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Coffee+Machines/Coffee+Machines/Coffee+Grinders/528/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Coffee+Machines/Coffee+Machines/Kettles/539/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Toasters/Toasters/Toasters/551/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Cooking+Appliances/Cooking+Appliances/Slow+Cookers/547/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Cooking+Appliances/Cooking+Appliances/Sandwich+Makers/548/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Cooking+Appliances/Cooking+Appliances/Fryers/534/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Cooking+Appliances/Cooking+Appliances/Bread+Makers/526/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Ironing/Ironing/Steam+Irons+and+Brushes/518/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Ironing/Ironing/Steam+Generators/1959/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Vacuum+Cleaners/Vacuum+Cleaners/All+Vacuum+Cleaners/5069/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Heaters+and+Fans/Heaters+and+Fans/Fans/488/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Hair+Care_2c+Shavers+and+Dental/Hair+Care_2c+Shavers+and+Dental/Hair+Dryers/688/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Hair+Care_2c+Shavers+and+Dental/Hair+Care_2c+Shavers+and+Dental/Hair+Straighteners/1975/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Hair+Care_2c+Shavers+and+Dental/Hair+Care_2c+Shavers+and+Dental/Hair+Stylers/1974/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Hair+Care_2c+Shavers+and+Dental/Hair+Care_2c+Shavers+and+Dental/Women's+Hair+Removal/702/ProductCategory.aspx",
"http://www.johnlewis.com/Electricals/Hair+Care_2c+Shavers+and+Dental/Hair+Care_2c+Shavers+and+Dental/Men's+Shavers/693/ProductCategory.aspx"]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories =  hxs.select('//*[@id="LHNCtl1_rptGp_ctl00_LHNGpCtl1_subnavac"]/ul/li/a/@href').extract()
        if categories:
            for category in categories:
                url =  urljoin_rfc(get_base_url(response), category)
                yield Request(url, callback=self.parse_products)
        else:
            yield Request(response.url, dont_filter=True, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//*[@id="SearchResultsGrid1_UpdatePanel1"]/div/div[@class="grid-item"]') 
        if products:
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)
                loader.add_xpath('name', 'div[@class="grid-copy"]/a[@class="gridtitle"]/text()')
                url = urljoin_rfc(get_base_url(response), product.select('div[@class="grid-copy"]/a[@class="gridtitle"]/@href').extract()[0])
                loader.add_value('url', url)
                price = ''.join(product.select('div[@class="grid-copy"]/a[@class="price"]/text()').extract()).split()[-1]
                loader.add_value('price', price)
                yield loader.load_item()
        next = hxs.select('//*[@id="paging"]/div[@class="pagenum"]/a[@class="next-pg"]/@href').extract()
        if next:
            url =  urljoin_rfc(get_base_url(response), next[0])
            yield Request(url, callback=self.parse_products)

