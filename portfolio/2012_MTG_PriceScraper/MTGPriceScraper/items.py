# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class MtgpricescraperItem(Item):
    # define the fields for your item here like:
    # name = Field()
    card_name = Field()
    magic_set = Field()
    page = Field()
    link = Field()
    low_price = Field()
    avg_price = Field()
    high_price = Field()
    store_name = Field()
    link_to_store = Field()
    price_in_store = Field()
    our_store_price = Field()
    items_in_our_store = Field()
    pass
