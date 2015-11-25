# Scrapy settings for sydney project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'sydney'

SPIDER_MODULES = ['sydney.spiders']
NEWSPIDER_MODULE = 'sydney.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'sydney (+http://www.yourdomain.com)'
DOWNLOAD_DELAY = 1
HTTPCACHE_ENABLED = True
