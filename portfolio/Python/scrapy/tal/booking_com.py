# -*- coding: utf-8 -*-
import datetime

from urllib import urlencode
from decimal import Decimal

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url
from scrapy.http import Request

from scrapy.utils.response import open_in_browser

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

search_url = 'http://www.booking.com/searchresults.html'

input_fields = {
    'destination_name': 'ssne',
    'checkin_day': 'checkin_monthday',
    'checkin_year_month': 'checkin_year_month',
    'checkout_day': 'checkout_monthday',
    'checkout_year_month': 'checkout_year_month',
    'adults': 'group_adults',
    'children': 'group_children',
    'si': 'si',
    'destination_type': 'dest_type',
    'destination_id': 'dest_id',
    'currency': 'selected_currency'
}

si = 'ai,co,ci,re,di'

cities = {
    'Tel Aviv, Israel': '-781545',
    'Jerusalem, Israel': '900000000',
    'Eilat, Israel': '-779626',
    'Haifa, Israel': '-780112',
    'Tiberias, Israel': '-781620',
    'Galilee, Israel': '900048031',
    'Arad, Israel': '-779238',
    'Ashqelon, Israel': '-779275',
    'Beer Sheva, Israel': '-779367',
    'Nahariyya, Israel': '-780813',
    'Nazareth, Israel': '780833',
    'Herzliya, Israel': '-780136',
    '‘Akko, Israel': '-779173',
    'Bat Yam, Israel': '-779349',
    'Netanya, Israel': '-780860',
    'Safed, Israel': '-781845',
    'Caesarea, Israel': '-781329',
    'Miẕpe Ramon, Israel': '-780762',
    'Ein Bokek, Israel': '-779680',
    'Rechovot, Israel': '-781210',
    'Ramat Gan, Israel': '-781147',
    'Bethlehem, Palestinian Territory': '900048785',
}

city_destination_type = 'city'


regions = {
    'Dead Sea Israel, Israel': '3230',
    'Sea of Galilee, Israel': '3643',
}
region_destination_type = 'region'


airports = {
    'Ben Gurion, Tel Aviv, Israel': '113',
}
airport_destination_type = 'airport'


landmarks = {
    'Ben Gurion University, Israel': '34179',
}
landmark_destination_type = 'landmark'

nights = 3

day_format = "%d"
year_month_format = "%Y-%m"

currency = 'USD'


class BookingComSpider(BaseSpider):
    name = "booking_com"
    allowed_domains = ["booking.com"]
    start_urls = (
        'http://www.booking.com/',
        )

    def parse(self, response):
        # calculate calendar values
        today = datetime.date.today()
        checkin_date = date_plus_1_month(today)
        checkout_date = checkin_date + datetime.timedelta(days=nights)

        params = {}
        params[input_fields['checkin_day']] = checkin_date.strftime(day_format)
        params[input_fields['checkin_year_month']] = checkin_date.strftime(year_month_format)
        params[input_fields['checkout_day']] = checkout_date.strftime(day_format)
        params[input_fields['checkout_year_month']] = checkout_date.strftime(year_month_format)
        params[input_fields['adults']] = '2'
        params[input_fields['children']] = '0'
        params[input_fields['si']] = si
        params[input_fields['currency']] = currency

        for city, city_id in cities.items():
            params[input_fields['destination_name']] = city
            params[input_fields['destination_type']] = city_destination_type
            params[input_fields['destination_id']] = city_id

            request_url = search_url + "?" + urlencode(params)

            request = Request(
                url=request_url,
                callback=self.parse_items
            )
            yield request

        for region, region_id in regions.items():
            params[input_fields['destination_name']] = region
            params[input_fields['destination_type']] = region_destination_type
            params[input_fields['destination_id']] = region_id

            request_url = search_url + "?" + urlencode(params)

            request = Request(
                url=request_url,
                callback=self.parse_items
            )
            yield request

        for airport, airport_id in airports.items():
            params[input_fields['destination_name']] = airport
            params[input_fields['destination_type']] = airport_destination_type
            params[input_fields['destination_id']] = airport_id

            request_url = search_url + "?" + urlencode(params)

            request = Request(
                url=request_url,
                callback=self.parse_items
            )
            yield request

        for landmark, landmark_id in landmarks.items():
            params[input_fields['destination_name']] = landmark
            params[input_fields['destination_type']] = landmark_destination_type
            params[input_fields['destination_id']] = landmark_id

            request_url = search_url + "?" + urlencode(params)

            request = Request(
                url=request_url,
                callback=self.parse_items
            )
            yield request

    def parse_items(self, response):
        hxs = HtmlXPathSelector(response)
        URL_BASE = get_base_url(response)
        next_page = hxs.select("//table[contains(@class, 'prevnextbar')]/tr/td[@class='next']/a/@href").extract()
        if next_page:
            new_url = urljoin_rfc(URL_BASE, next_page[0])
            request = Request(
                url=new_url,
                callback=self.parse_items
            )
            yield request

        items = hxs.select("//table[@class='hotellist']/tr[contains(@class, 'flash_deal_soldout')]")
        for item in items:
            # getting hotel information
            hotel_name = item.select("td[2]/h3/a/text()").extract()[0]
            hotel_url = item.select("td[2]/h3/a/@href").extract()[0]
            hotel_url = urljoin_rfc(URL_BASE, hotel_url)

            # getting rooms list
            rooms = []
            price_rows = item.select("td[2]/div/form/table/tbody/tr")
            for price_row in price_rows:
                max_persons = price_row.select("td[@class='maxPersons']/div/span[@class='hideme']/text()").extract()[0]
                if int(max_persons) != 2:
                    # skip if room is not for 2 persons
                    continue
                room_name = price_row.select("td[@class='roomName']/div/a/text()").extract()[0]
                room_url = price_row.select("td[@class='roomName']/div/a/@href").extract()[0]
                room_price = price_row.select("td[@class='roomPrice']/div/strong[contains(@class, 'price')]/text()").re("[\d.]+")
                if not room_price:
                    logging.error("NO PRICE! '%s' %s" % (response.url, hotel_name))
                    continue
                room_price = Decimal(room_price[0])
                rooms.append({
                    'name': room_name,
                    'url': room_url,
                    'price': room_price
                })

            # searching for room with minimum price
            if rooms:
                room_min = rooms[0]
                for room in rooms:
                    if room['price'] < room_min['price']:
                        room_min = room

                l = ProductLoader(item=Product(), response=response)
                l.add_value('name', hotel_name.encode('ascii', 'replace'))
                l.add_value('identifier', hotel_name.encode('ascii', 'replace'))
                l.add_value('url', hotel_url)
                l.add_value('price', room_min['price'])
                yield l.load_item()
