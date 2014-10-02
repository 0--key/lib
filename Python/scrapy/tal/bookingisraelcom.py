# -*- coding: utf-8 -*-
import datetime
import os
import urllib
import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from scrapy.http import Request
from product_spiders.utils import extract_price2uk
from product_spiders.items import Product, ProductLoader

import logging


def date_plus_1_month(date_obj):
    month = date_obj.month
    year = date_obj.year
    if month == 12:
        new_year = year + 1
        new_month = 1
    else:
        new_year = year
        new_month = month + 1

    day = date_obj.day

    future = None
    while not future:
        try:
            future = datetime.date(new_year, new_month, day)
        except ValueError:
            day -= 1

    return future

allowed_cities = [
    "JRS",
    "TLV",
    "DEAD",
    "ETH",
    "HFA",
    "TIBE",
    "GAL16",
    "ARAD",
    "ASHQ",
    "BEV",
    "NAHA",
    "BETL",
    "NAZE",
    "HERZ",
    "ACRE",
    "BATY",
    "NETA",
    "SAFE",
    "CAES",
    "UPPE",
    "MIZP",
    ]

nights = 3

url = 'http://www.bookingisrael.com'
search_url = 'http://www.bookingisrael.com/Search/'
user_agent = 'Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1'
request_body_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "request_body")

day_format = "%d"
year_month_format = "%Y-%m"

currency = 'USD'


class BookingComSpider(BaseSpider):
    name = "bookingisrael.com"
    allowed_domains = ["bookingisrael.com"]
    start_urls = (
        'http://www.bookingisrael.com/',
        )

    headers = {
        'User-agent': user_agent
    }
    form_headers = {
        'User-agent': user_agent,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    formdata = {}

    def parse(self, response):
        headers = {'User-agent': user_agent}

        # opening main page for cookies
        yield Request(url, dont_filter=True, headers=headers, callback=self.collect_cookies, meta={'dont_merge_cookies': True})

    def collect_cookies(self, response):
        hxs = HtmlXPathSelector(response)
        view_state = self.get_view_state(hxs)

        # calculate calendar values
        check_in_date = date_plus_1_month(datetime.date.today())
        check_out_date = check_in_date + datetime.timedelta(days=nights)
        handle = open(request_body_filename, 'r')
        request_body = handle.read()
        handle.close()

        request_body = request_body.replace("%%%CHECK_IN_DATE%%%", check_in_date.strftime("%d.%m.%Y"))
        request_body = request_body.replace("%%%CHECK_OUT_DATE%%%", check_out_date.strftime("%d.%m.%Y"))
        request_body = request_body.replace("%%%NIGHTS%%%", str(nights))
        request_body = request_body.replace("%%%VIEWSTATE%%%", urllib.quote(view_state).replace("/", "%2F"))
        self.request_body = request_body

        self.formdata = {
            'Signup': '',
            '__ASYNCPOST': 'true',
            '__EVENTARGUMENT': '',
            '__EVENTTARGET': 'ctl05$ctl07$btnSearch',
            '__VIEWSTATE': view_state,
            'choose': 'on',
            'ctl05$ctl02$Password': '',
            'ctl05$ctl07$Calendar1$dateCheckIn': check_in_date.strftime("%d.%m.%Y"),
            'ctl05$ctl07$Calendar1$dateCheckOut': check_out_date.strftime("%d.%m.%Y"),
            'ctl05$ctl07$Calendar1$hiddenfieldCheckIn': check_in_date.strftime("%d.%m.%Y"),
            'ctl05$ctl07$Calendar1$hiddenfieldCheckOut': check_out_date.strftime("%d.%m.%Y"),
            'ctl05$ctl07$Calendar1$hiddenfieldNights': str(nights),
            'ctl05$ctl07$Calendar1$nightsDDL': str(nights),
            'ctl05$ctl07$CityCodeByHotel': '',
            'ctl05$ctl07$m_city1': '',
            'ctl05$ctl07$tbHotel': '',
            'scriptMgr': 'ctl05$ctl05|ctl05$ctl07$btnSearch'
        }

        self.cities = allowed_cities[:]

        yield self.get_city_request()

    def get_city_request(self):
        try:
            city = self.cities.pop()
        except IndexError:
            return None

        cur_formdata = self.formdata.copy()
        cur_formdata['ctl05$ctl07$m_city1'] = city
        cur_request_body = self.request_body.replace("%%%CITY%%%", city)
        # sending search request. results will be downloaded after next request
        logging.error("Searching city: %s" % city)
        request = Request(
            url=url,
            method="POST",
            body=cur_request_body,
            dont_filter=True,
            headers=self.form_headers,
            callback=self.redirect_search
        )
        return request

    def redirect_search(self, response):
        """
        Parses body of page with results
        """
        hxs = HtmlXPathSelector(response)

        yield Request(
            url=search_url,
            dont_filter=True,
            headers=self.headers,
            callback=self.parse_search
        )

    def parse_search(self, response):
        hxs = HtmlXPathSelector(response)

        count_el = hxs.select("//table[@id='ctl05_myContainer']/tr[3]/td[2]/div[@id='ctl05_ctl12']/h1/text()").extract()

        count = '0'
        for el in count_el:
            m = re.search("[\d]+", el)
            if m:
                count = m.group(0)
            else:
                count = '0'
        logging.error("Found %s hotels" % count)

        hotels = hxs.select("//div[@id='divResults']/div[@class='accomodation grey'] | \
                                  //div[@id='divResults']/div[@class='accomodation']")
        for hotel in hotels:
            name = hotel.select("div[1]/h4/a/text()").extract()
            if not name:
                logging.error("No name")
            name = name[0]

            url = hotel.select("a[1]/@href").extract()
            if not url:
                logging.error("No url %s")
            url = url[0]

            price = hotel.select("div[@class='price']/span[@class='sum2']/text()").extract()
            if not price:
                logging.error("No price")
            price = price[0]
            price = extract_price2uk(price)
            if price is None:
                print "No price %s" % name
                continue
            price = int(price)*nights

            l = ProductLoader(item=Product(), response=response)
            l.add_value('name', name.encode('ascii', 'replace'))
            l.add_value('identifier', name.encode('ascii', 'replace'))
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()

        yield self.get_city_request()

    def get_view_state(self, hxs):
        view_state = hxs.select("//input[@id='__VIEWSTATE']/@value").extract()
        if view_state:
            return view_state[0]
        else:
            return None
