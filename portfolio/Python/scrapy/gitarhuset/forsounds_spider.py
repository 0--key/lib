from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy import log

from product_spiders.items import Product, \
    ProductLoaderWithNameStrip as ProductLoader


class ForSoundsSpider(BaseSpider):
    name = "4sound.no"
    allowed_domains = ['4sound.no']
    start_urls = ['http://www.4sound.no',]

    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        catlurls = hxs.select("//div[@id='l_nav']/ul[1]//a/@href").extract()

        for catlurl in catlurls:
             yield Request(urljoin_rfc(base_url, catlurl), \
                          callback=self.parse_section_maingroup)


    def parse_section_maingroup(self, response):
        hxs = HtmlXPathSelector(response)

        sectionurls = hxs.select("//div[@id='l_nav2']//a/@href").extract()

        for sectionurl in sectionurls:
             yield Request(urljoin_rfc('http://www.4sound.no', sectionurl), \
                            callback=self.parse_section)


    def parse_section(self, response):
        hxs = HtmlXPathSelector(response)
        producturls = hxs.select("//div[@id='mainContent']//table//a/@href").extract()
        for producturl in producturls:
            log.msg('product url %s' % producturl)
            yield Request(urljoin_rfc('http://www.4sound.no', producturl), \
                            callback=self.parse_product)


        if "javascript:__doPostBack('_ctl0$_ctl0$MainContent$MainContent$Linkbutton3','')" in producturls:
            formname = 'aspNetForm'
            formdata = {'__EVENTTARGET':
                        '_ctl0$_ctl0$MainContent$MainContent$Linkbutton3',
                        '__EVENTARGUMENT': ''}
            request = FormRequest.from_response(response, formname=formname,
                                                formdata=formdata,
                dont_click=True, callback=self.parse_section)
            yield request



    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        loader = ProductLoader(response=response, item=Product())
        log.msg("%s %s %s" % (response.url,
                              hxs.select("//span[@class='itempgHeadline']/text()").extract(),
                              hxs.select("//span[@class='pris_base']/text()").extract()))

        price = hxs.select("//span[@class='pris_base']/text()").extract()
        if not response.url.startswith('javascript') and price:
            str_price = price[0].split(' ')[-1][:-2]
            price = int(float(str_price) * 1000) if '.' \
                in str_price else int(str_price)
            
            loader.add_xpath('name', "//span[@class='itempgHeadline']/text()")
            loader.add_value('url', response.url)
            loader.add_value('price', price)

            yield  loader.load_item()

