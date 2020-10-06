from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader


class JohnLewisSpider(BaseSpider):
    name = 'johnlewis.com-johnlewis'
    allowed_domains = ['johnlewis.com']
    start_urls = ['http://www.johnlewis.com/Electricals/Televisions/Televisions/All+TVs/5013/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/Blu-ray_2c+DVD+and+Home+Cinema/Blu-ray_2c+DVD+and+Home+Cinema/View+all+Cinema+Systems/78/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/Blu-ray_2c+DVD+and+Home+Cinema/Blu-ray_2c+DVD+and+Home+Cinema/Blu-ray+Players/4741/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/Blu-ray_2c+DVD+and+Home+Cinema/Blu-ray_2c+DVD+and+Home+Cinema/View+all+Digital+Recorders/24486/           ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/Freeview+and+Freesat+Boxes/Freeview+and+Freesat+Boxes/Freeview+and+Freesat+Boxes/98/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/TV+Stands+and+Accessories/3D+Glasses+and+Transmitters/3D+Glasses+and+Transmitters/16022/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/Cameras+and+Camcorders/Cameras+and+Camcorders/All+Cameras/4002/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/Audio/All+Radios/View+all+Radios/1842/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/Audio/Speaker+Docks/Speaker+Docks/22775/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/Audio/Micro+Systems/Micro+Systems/52/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/Audio/Wireless+Music+Players/Wireless+Music+Players/1332/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/Audio/iPods+and+MP3+Players/Apple+iPods/1379/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/Headphones/Headphones/View+all+headphones/660/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/Kindle+and+eReaders/eBook+Readers/eBook+Readers/8957/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/iPad+and+Tablet+PCs/View+all+Tablets/View+all+Tablets/21438/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/Laptops+and+Netbooks/Laptops+and+Netbooks/Laptops/398/ProductCategory.aspx',
                  'http://www.johnlewis.com/Electricals/Telephones/All+Telephones/All+Telephones/22237/ProductCategory.aspx']

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

