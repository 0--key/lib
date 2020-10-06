import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class ScentimentsWebSpider(BaseSpider):
    name = "scentiments.com"
    allowed_domains = ["scentiments.com", "www.scentiments.com"]
    start_urls = ("http://www.scentiments.com/Product/CategoryInfo.aspx?cid=24",)

    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        designer_urls = hxs.select('//table[contains(@id,"AllBrandsModule")]//td//a/@href').extract()

        for designer_url in designer_urls:
            m = re.search(r'name=(.+)', designer_url)
            if(m):
                join_url = "http://www.scentiments.com/Custom/DesignerSkuList.aspx?Name=" + m.group(1)
                yield Request(join_url, callback=self.parse_designer)
        
    def parse_designer(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//table//tr[descendant::a]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            url = product.select('.//td[@valign="Middle"]/a[contains(@href,"Product")]/@href')[0]
            loader.add_value('url', urljoin_rfc(base_url, url.extract()))
            loader.add_xpath('name', './/td[@valign="Middle"]/a/span/text()')
            loader.add_xpath('price', './/td/p/b/text()')
#            sku = product.select('//div[@id="productDetail"]//p[1]')[0].re('Ref\. Code: (\d+)')
            loader.add_value('sku', url.re('id=(\d+)')[0])
            yield loader.load_item()
