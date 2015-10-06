from scrapy.http import Request
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest
from scrapy.contrib.loader import XPathItemLoader

import spynner

browser = spynner.Browser()
        
class InitialSpider(BaseSpider):
    name = 'initialspider'
    start_urls = ["http://www.impactguns.com/category.aspx?zcid=238"]
    
    def parse(self, response):
	start_url = "http://www.impactguns.com/category.aspx?zcid=238"    
	browser.load(start_url)    
	hxs = HtmlXPathSelector(browser.html)

    def test_parse(self, response):
        self.log("This is page iteration")

"""        hxs = HtmlXPathSelector(response)
        requests = []
        for page_num in range(35):
            requests.append(FormRequest.from_response(
                response,
                formdata={'ctl00$ctl00$MainContent$uxCategory$uxCategoryProductList$ddPageNum':page_num},
                callback=self.test_parse
                )
                            )
        for request in requests:
            yield request
"""
