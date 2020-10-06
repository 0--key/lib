from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader

import logging


class ArgosCoUkSagemcomSpider(BaseSpider):
    name = 'argos.co.uk_sagemcom'
    allowed_domains = ['argos.co.uk']
    start_urls = (
        'http://www.argos.co.uk/',
        )
    search_url = 'http://www.argos.co.uk/webapp/wcs/stores/servlet/Search?pp=Show+all&s=Relevance&storeId=10001&catalogId=1500002901&langId=-1&q='

    keywords = ['Sagemcom', 'Sagem']

    products = [
        'http://www.argos.co.uk/static/Search/searchTerms/HUMAX+HDR-+FOX+500GB+T2.htm',
        'http://www.argos.co.uk/static/Search/searchTerms/PANASONIC+DMR+HW100+320GB.htm',
        'http://www.argos.co.uk/static/Search/searchTerms/SAMSUNG+SMT+S7800+FREESAT+500GB.htm',
        'http://www.argos.co.uk/static/Product/partNumber/5322910/Trail/searchtext%3ESAGEMCOM.htm',
        'http://www.argos.co.uk/static/Product/partNumber/5323012/Trail/searchtext%3EHUMAX.htm',
        'http://www.argos.co.uk/static/Search/searchTerms/SONY+SVR+HDT500.htm',
        'http://www.argos.co.uk/static/Search/searchTerms/PPX+2055.htm',
        'http://www.argos.co.uk/static/Product/partNumber/9296224/Trail/searchtext%3E1230.htm',
        'http://www.argos.co.uk/static/Search/searchTerms/PPX+1430.htm',
        'http://www.argos.co.uk/static/Product/partNumber/6833680.htm',
        'http://www.argos.co.uk/static/Product/partNumber/044361.htm',
        'http://www.argos.co.uk/static/Search/searchTerms/PK120+OPTOMA.htm',
        'http://www.argos.co.uk/static/Product/partNumber/9046797.htm?cmpid=GG05X&_$ja=kw:acer+c110|cgn:Projectors%7c%7cAcer+c110+pico+projector%7c%7c9046797|cgid:2353050677|tsid:13542|cn:NB%7c%7cS%7c%7cPPCPM%7c%7cProduct%7c%7cProjectors+and+screens|cid:72584117|lid:99520637|mt:Exact|nw:search|crid:10235505317',
        'http://www.argos.co.uk/static/Product/partNumber/9046807.htm',
        'http://www.argos.co.uk/static/Product/partNumber/5323067/c_1/1%7Ccategory_root%7CHome+entertainment+and+sat+nav%7C14419512/c_2/2%7C14419512%7CDigital+boxes+and+services%7C14419633/c_3/3%7Ccat_14419633%7CDigital+TV+recorders%7C28608209.htm',
        ]

    def start_requests(self):
        for keyword in self.keywords:
            url = self.search_url + keyword
            request = Request(url, callback=self.parse_search)
            yield request

        for url in self.products:
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        url = response.url

        name = hxs.select("//h1[@class='fn']/text()").extract()
        if not name:
            logging.error("ERROR! NO NAME! %s" % url)
            return
        name = name[0]

        price = hxs.select("//div[@id='content']//div[@id='pdpPricing']/span[@class='actualprice']/span[@class='price']/text()").extract()
        if not price:
            logging.error("ERROR! NO PRICE! %s %s" % (url, name))
            return
        price = price[0]

        l = ProductLoader(item=Product(), response=response)
        l.add_value('identifier', name)
        l.add_value('name', name)
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()

    def parse_search(self, response):
        hxs = HtmlXPathSelector(response)

        items = hxs.select("//div[@id='content']/div[@id='searchcontent']/div[@class='hasResults']/form/div[@id='switchview']/ol/li")
        for item in items:
            name = item.select("ul/li[@class='producttitle']/h4/a[1]/text()").extract()
            if not name:
                continue
            name = name[0]
            url = item.select("ul/li[@class='producttitle']/h4/a[1]/@href").extract()
            if not url:
                logging.error("ERROR! NO URL! URL: %s. NAME: %s" % (response.url, name))
                continue
            url = url[0]
            price = item.select("ul/li[contains(@class, 'pricing')]/ul/li[contains(@class, 'price')]/text()").extract()
            if not price:
                logging.error("ERROR! NO PRICE! URL: %s. NAME: %s" % (response.url, name))
                continue
            price = price[0]

            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', name)
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()
