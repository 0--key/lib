# -*- coding: utf-8 -*-
from __future__ import with_statement

try:
    import json
except ImportError:
    import simplejson as json
import datetime
import math
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest
from product_spiders.items import Product, ProductLoader

from scrapy.utils.response import open_in_browser

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

cities = [
    "Akko, Israel",
    "Almog, West Bank and Gaza",
    "Arad, Israel",
    "Ashkelon, Israel",
    "Bat Yam, Israel",
    "Beersheba, Israel",
    "Be'er Ya'akov, Israel",
    "Bethlehem, West Bank and Gaza",
    "Caesarea, Israel",
    "Dor, Israel",
    "Eilat (and vicinity), Israel",
    "Ein Bokek, Israel",
    "Ein Gedi, Israel",
    "Ein Gev, Israel",
    "Ginosar, Israel",
    "Gonen, Israel",
    "Haifa, Israel",
    "Herzliya, Israel",
    "Jerusalem (and vicinity), Israel",
    "Kfar Blum, Israel",
    "Kfar Giladi, Israel",
    "Lavi, Israel",
    "Ma'alot - Tarshiha, Israel",
    "Maagan, Israel",
    "Ma'ale Hachamisha, Israel",
    "Mitzpe Ramon, Israel",
    "Nahsholim, Israel",
    "Nahariya, Israel",
    "Nazareth, Israel",
    "Netanya, Israel",
    "Neve Ativ, Israel",
    "Newe Ilan, Israel",
    "Neve Zohar, Israel",
    "Ramat Gan, Israel",
    "Ramot, Israel",
    "Rosh Pinna, Israel",
    "Hazor Haglilit, Israel",
    "Safed, Israel",
    "Shavei Zion, Israel",
    "Shefayim, Israel",
    "Shoresh, Israel",
    "Tel Aviv (and vicinity), Israel",
    "Tiberias, Israel",
    "Tzuba, Israel",
    "Yesod HaMa'ala, Israel"
]

nights = 3

date_format = '%m/%d/%Y'

class ExpediaComSpider(BaseSpider):
    name = "expedia.com"
    allowed_domains = ["expedia.com"]
    start_urls = (
        'http://www.expedia.com/Hotels',
        )

    search_url = 'http://www.expedia.com//Hotel-Search'
    pages_url = 'http://www.expedia.com/Hotel-Search-AJAX?action=filterSearch'

    def parse(self, response):
        # calculate calendar values
        today = datetime.date.today()
        checkin_date = date_plus_1_month(today)
        checkout_date = checkin_date + datetime.timedelta(days=nights)

        for city in cities:

            params = {}

            params['action'] = 'hotelSearchWizard@searchHotelOnly'
            params['hotelSearchWizard_inpItid'] = ''
            params['hotelSearchWizard_inpItty'] = ''
            params['hotelSearchWizard_inpItdx'] = ''
            params['hotelSearchWizard_inpSearchMethod'] = ''
            params['hotelSearchWizard_inpSearchKeywordIndex'] = ''
            params['hotelSearchWizard_inpSearchKeyword'] = ''
            params['hotelSearchWizard_inpSearchRegionId'] = ''
            params['hotelSearchWizard_inpSearchLatitude'] = ''
            params['hotelSearchWizard_inpSearchLongitude'] = ''
            params['hotelSearchWizard_inpSearchNearType'] = 'CITY'
            params['hotelSearchWizard_inpSearchNear'] = city
            params['hotelSearchWizard_inpSearchNearStreetAddr'] = ''
            params['hotelSearchWizard_inpSearchNearCity'] = ''
            params['hotelSearchWizard_inpSearchNearState'] = ''
            params['hotelSearchWizard_inpSearchNearZipCode'] = ''
            params['hotelSearchWizard_inpCheckIn'] = checkin_date.strftime(date_format)
            params['hotelSearchWizard_inpCheckOut'] = checkout_date.strftime(date_format)
            params['hotelSearchWizard_inpNumRooms'] = '1'
            params['hotelSearchWizard_inpNumAdultsInRoom'] = '2'
            params['hotelSearchWizard_inpNumChildrenInRoom'] = '0'
            params['hotelSearchWizard_inpAddOptionFlag'] = 'false'
            params['hotelSearchWizard_inpHotelName'] = ''
            params['hotelSearchWizard_inpHotelClass'] = '0'
            params['searchWizard_wizardType'] = 'hotelOnly'

            request = FormRequest(self.search_url, formdata=params, callback=self.parse_items)
            yield request

    def parse_items(self, response):
        hxs = HtmlXPathSelector(response)

        search_params = hxs.select("//script").re(u'\\\\"searchWizard\\\\":(.*?),[\s]*\\\\"searchWizardInitial\\\\"')
        search_params = json.loads(search_params[0].replace(r'\"', r'"'))['d']
        region = search_params[11]
        regionId = search_params[23]
        inpCity = search_params[13]
        inpCityForHotelGroup = inpCity
        parentRegion = search_params[24]
        inpTotalCount = search_params[26]
        inpStartDate = search_params[5]
        inpEndDate = search_params[6]

        offersPerPage = 25

        for inpPageIndex in range(0, int(math.ceil(float(inpTotalCount) / offersPerPage)) + 1):
            params = {}
            params['inpRfrrId'] = '-56907'
            params['inpRoomAvailsOpenedState'] = ''
            params['inpGetFilterCounts'] = ''
            params['inpCityForHotelGroup'] = inpCityForHotelGroup
            params['hotelChainId'] = ''
            params['inpHotelName'] = ''
    #        params['hidRegionId'] = '180031'
            params['lodgingTypeId'] = '0'
            params['selSortType'] = '0'
            params['inpPaginationRequest'] = '1'
            params['inpPageIndex'] = str(inpPageIndex * offersPerPage)
            params['offersPerPage'] = str(offersPerPage)
            params['regionId'] = regionId
            params['region'] = region
            params['parentRegion'] = parentRegion
            params['latLong'] = ''
            params['inpTotalCount'] = str(inpTotalCount)
            params['inpRegionType'] = 'CITY'
            params['inpCity'] = inpCity
            params['inpStartDate'] = inpStartDate
            params['inpEndDate'] = inpEndDate
            params['roomCountInput'] = '1'
            params['adultCountInput'] = '2'
            params['childCountInput'] = '0'
            request = FormRequest(self.pages_url, formdata=params, callback=self.parse_pages)
            yield request

        return

    def parse_pages(self, response):
        result = json.loads(response.body)

        items = result['retailHotelModelListFirst']['d'][0] + result['retailHotelModelListLast']['d'][0]

        products = 0
        for item in items:
            item = item['d']

            name = item[0]['d'][5]
            price = item[1]['d'][2]
            url = item[-1]
            if price:
                price = float(price) * nights
                l = ProductLoader(item=Product(), response=response)
                l.add_value('name', name.encode('ascii', 'replace'))
                l.add_value('identifier', name.encode('ascii', 'replace'))
                l.add_value('url', url)
                l.add_value('price', price)
                yield l.load_item()
                products += 1