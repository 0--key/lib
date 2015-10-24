# Scrapy settings for krak project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'krak'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['krak.spiders']
NEWSPIDER_MODULE = 'krak.spiders'
DEFAULT_ITEM_CLASS = 'krak.items.KrakItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

