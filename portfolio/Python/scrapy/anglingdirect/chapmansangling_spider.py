import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class summerlandstackle_spider(BaseSpider):
    name = 'chapmansangling.co.uk'
    allowed_domains = ['chapmansangling.co.uk', 'www.chapmansangling.co.uk']
    start_urls = ('http://www.chapmansangling.co.uk',)

    def parse_product(self, response):
        base_url = get_base_url(response)
        
        hxs = HtmlXPathSelector(response)
        res = {}
        products = hxs.select("//div[@class='product_small_rod']/form")
        for p in products:
            options = p.select(".//div[@class='rod_inset']/p[@class='vat']/select/option/text()").extract()
            if options:
                #options
                name = p.select(".//div[@class='rod_inset']/a/h3[@class='coarse']/text()")[0].extract().strip()
                url = p.select(".//div[@class='rod_inset']/a/@href")[0].extract()
                for option in options:
                    name2 = re.match(r'(.*) \(.*\) \(',option).group(1)
                    price = re.match(r'.*\(\xa3(.*)\)',option).group(1)
                    res['url'] = urljoin_rfc(base_url,url)
                    res['description'] = name + u' ' + name2
                    res['price'] = price
                    yield load_product(res, response)
            else:
                name = p.select(".//div[@class='rod_inset']/a/h3[@class='coarse']/text()")[0].extract().strip()
                url = p.select(".//div[@class='rod_inset']/a/@href")[0].extract()
                price = "".join(p.select(".//span[@class='bigprice']/text()").re(r'([0-9\,\. ]+)')).strip()
                res['url'] = urljoin_rfc(base_url,url)
                res['description'] = name
                res['price'] = price
                yield load_product(res, response)   

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//ul[@id="product-nav"]/li/a/@href').extract()
        for url in category_urls:
            yield Request(urljoin_rfc(base_url,url))
            
        #additional categories
        acategory_urls = hxs.select('//table[@class="coarse-subnav"]/tr/td/div/a/@href').extract()
        for aurl in acategory_urls:
          yield Request(urljoin_rfc(base_url,aurl))
            
        # products
        for p in self.parse_product(response):
            yield p