# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class SupplierItem(Item):
    trading_name = Field()
    stall_location = Field()
    phone = Field()
    fax = Field()
    products_sold = Field()
