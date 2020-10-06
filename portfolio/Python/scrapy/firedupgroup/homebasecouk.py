from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader
from scrapy import log

PROXY = 'http://ec2-107-20-62-101.compute-1.amazonaws.com:6543'

def proxyRequest(*args, **kwargs):
    meta = {'proxy': PROXY}
    if 'meta' in kwargs:
        kwargs['meta'].update(meta)
    else:
        kwargs['meta'] = meta
    return Request(*args, **kwargs)


class HomebaseCoUkSpider(BaseSpider):
    name = 'homebase.co.uk'
    allowed_domains = ['homebase.co.uk']
    start_urls = ('http://www.homebase.co.uk/webapp/wcs/stores/servlet/Browse?storeId=10151&langId=110&c_1=1|category_root|Heating+and+Cooling|16849264&c_2=2|cat_16849264|Fireplaces+and+Stoves|14289968',)

    start_urls = (
        'http://www.homebase.co.uk/webapp/wcs/stores/servlet/Browse?storeId=10151&langId=110&c_2=2%7Ccat_16849264%7CFireplaces+and+Stoves%7C14289968&c_1=1%7Ccategory_root%7CHeating+and+Cooling%7C16849264&c_3=3|cat_14289968|Fireplace+Suites|14289979',
        'http://www.homebase.co.uk/webapp/wcs/stores/servlet/Browse?storeId=10151&langId=110&c_2=2%7Ccat_16849264%7CFireplaces+and+Stoves%7C14289968&c_1=1%7Ccategory_root%7CHeating+and+Cooling%7C16849264&c_3=3|cat_14289968|Accessories+and+Fuel|14290330',
        'http://www.homebase.co.uk/webapp/wcs/stores/servlet/Browse?storeId=10151&langId=110&c_2=2%7Ccat_16849264%7CFireplaces+and+Stoves%7C14289968&c_1=1%7Ccategory_root%7CHeating+and+Cooling%7C16849264&c_3=3|cat_14289968|Fire+Surrounds|14289977',
        'http://www.homebase.co.uk/webapp/wcs/stores/servlet/Browse?storeId=10151&langId=110&c_2=2%7Ccat_16849264%7CFireplaces+and+Stoves%7C14289968&c_1=1%7Ccategory_root%7CHeating+and+Cooling%7C16849264&c_3=3|cat_14289968|Stoves|14289989',
        'http://www.homebase.co.uk/webapp/wcs/stores/servlet/Browse?storeId=10151&langId=110&c_2=2%7Ccat_16849264%7CFireplaces+and+Stoves%7C14289968&c_1=1%7Ccategory_root%7CHeating+and+Cooling%7C16849264&c_3=3|cat_14289968|Inset+Fires|14289969',
        'http://www.homebase.co.uk/webapp/wcs/stores/servlet/Browse?storeId=10151&langId=110&c_2=2%7Ccat_16849264%7CFireplaces+and+Stoves%7C14289968&c_1=1%7Ccategory_root%7CHeating+and+Cooling%7C16849264&c_3=3|cat_14289968|Wall+Mounted+Fires|14289971',
    )

    download_delay = 2

    def parse(self, response):
        URL_BASE = get_base_url(response)
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select("//div[@id='subnav']/ul[@class='brand attributes']//a/@href").extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        pages_urls = hxs.select("//div[@class='paginglinks']").extract()
        for url in pages_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        products_els = hxs.select("//li[@class='product']")
        log.msg("%s products found" % len(products_els))
        for product_el in products_els:
            name = product_el.select("h4/a/text()").extract()
            if not name:
                log.msg('ERROR!! NO NAME!! %s' % response.url)
                continue
            name = name[0]

            url = product_el.select("h4/a/@href").extract()
            if not url:
                log.msg('ERROR!! NO URL!! %s' % response.url)
                continue
            url = url[0]
            url = urljoin_rfc(URL_BASE, url)

            price = product_el.select("ul[@class='pricing']/li[@class='price']/text()").extract()
            if not price:
                log.msg('ERROR!! NO PRICE!! %s' % response.url)
                continue
            price = price[0]

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)

            loader.add_value('sku', '')

            yield loader.load_item()
