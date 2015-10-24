from urlparse import urljoin

from scrapy.http import Request
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from krak.items import KrakItem

import urllib
import urllib2
import sys
import os

def extract_short_description(dirty_sd_list):
    clean_shd = []
    for i in dirty_sd_list:
        shd = i.split('<div class="companyinfo">\n')[-1].strip().split('</div>')[0].strip()
        if '"column grid-30"' in shd:
            clean_shd.append("Not specified")
        else:
            clean_shd.append(shd)
    return clean_shd

def extract_links_to_c_s(dirty_sourse):
    clean_ltcs = []
    for j in dirty_sourse:
        link = j.split('<h3><a href="')[-1].split('"')[0]
        if "<div class=" in link:
            clean_ltcs.append("Company site unknown")
        else:
            clean_ltcs.append(link)
    return clean_ltcs

def clear_gd(raw_gd_list):
    clean_gd = []
    for jt in raw_gd_list:
        clean_gd.append(jt.strip())
    return clean_gd

class InitialSpider(BaseSpider):
    name = 'initialspider'
    DOWNLOAD_DELAY = 5
    list_of_pages = ['http://www.krak.dk/s%C3%B8geord/vikarbureauer:30764',]
    for c in range(62,67):
        list_of_pages.append("http://www.krak.dk/s%C3%B8geord/vikarbureauer:30764/p:"+str(c))    
    start_urls = list_of_pages
    company_counter = {}
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        company_names = hxs.select('//div[@class="row body"]//div[@class="column grid-64"]//div[@class="row header"]//h2/a/text()').extract()
        links = hxs.select('//div[@class="row body"]//div[@class="column grid-64"]//div[@class="row header"]//h2/a/@href').extract()
	links_to_companies_sites = hxs.select('//div[@class="row body"]//div[@class="column grid-64"]//div[@class="row header"]//h3/a/@href').extract()
	short_description_source = hxs.select('//div[@class="column grid-30"]//div[@class="row"]//div[@class="column grid-30"]').extract()
        clear_short_description = extract_short_description(short_description_source)
        if len(company_names)==len(links_to_companies_sites):
            self.log("This page is filled correctly")
        else:
            # need to extract links to companies sites manually
            raw_links_to_sites = hxs.select('//div[@class="row body"]//div[@class="column grid-64"]//div[@class="row header"]').extract()
            links_to_companies_sites = extract_links_to_c_s(raw_links_to_sites)
        companies_zip = zip(company_names, links, links_to_companies_sites, clear_short_description)
        for companies in companies_zip[3:5]:
            full_url = urljoin('http://www.krak.dk', companies[1])
            request = Request(full_url, callback = self.extractDetails)
            request.meta['company_name'] = companies[0]
            request.meta['company_site_url'] = companies[2]
            request.meta['short_description'] = companies[3]
            yield request

    def extractDetails(self, response):
        company_name = response.request.meta["company_name"]
        company_site_url = response.request.meta["company_site_url"]
        short_description = response.request.meta["short_description"]
        hxs = HtmlXPathSelector(response)
        address = hxs.select("//div[@id='content' and @class='col1']/div[1][@class='desc']/div[3][@class='contact folded']/dl[@class='default']/dd[2]/em/text()").extract()
        phone = hxs.select("//div[@id='content' and @class='col1']/div[@class='desc']/div[@class='contact folded']/dl[@class='default']/dd/span/text()").extract()
        phone_type = hxs.select("//div[@id='content' and @class='col1']/div[1][@class='desc']/div[3][@class='contact folded']/dl[@class='default']/dd[3]/em/text()").extract()
        raw_gen_description = hxs.select("//div[@id='content' and @class='col1']//div[@class='info']/p/text()").extract()
        tags = '###'.join(hxs.select("//div[@id='keywords' and @class='keywords no-print']//p[@class='toggle']//em[@class='original content']/a/text()").extract())
        category = hxs.select("//div[@id='pp-section-categories' and @class='categories']/ul/li/a/text()").extract()
        description_headers = '###'.join(hxs.select("//div[@id='slideshow-container' and @class='slideshow-container slideshow-profilepage no-print']//h3/text()").extract())
        description_paragraphs = '###'.join(hxs.select("//div[@id='slideshow-container' and @class='slideshow-container slideshow-profilepage no-print']//p/text()").extract())
        items = []
        item = KrakItem()
        item['company_name'] = company_name
        item['company_site_url'] = company_site_url
        item['short_description'] = short_description
        item['address'] = address
        item['phone'] = phone
        item['phone_type'] = phone_type
        item['gen_description'] = '###'.join(clear_gd(raw_gen_description))
        item['description_headers'] = description_headers
        item['description_paragraphs'] = description_paragraphs
        item['tags'] = tags
        item['category'] = category
        items.append(item)
        return items

        
"""
    
            # lets download images:
            image_name = companies[1].split('/')[-1]
            if image_name:
                f = open(str('logo/'+image_name), 'wb')
                f.write(urllib.urlopen(companies[1]).read())
                f.close()
        item = KrakItem()
        item['company_name'] = companies[0]
        item['logo_url'] = companies[1]
        item['local_link'] = companies[2]
        item['link_to_company_site'] = companies[3]
        item['short_description'] = companies[4]
        items.append(item)
        return items
"""
