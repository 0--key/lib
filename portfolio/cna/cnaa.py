import sys
import requests
from lxml import html


def main(argv):
    # compose url:
    query = argv[0]
    prefix = "http://www.bing.com/news/search?q=entertainment+news+"
    suffix = "&qs=n&form=NWRFSH&pq=entertainment+news+ozz&sc=0-20&sp=-1&sk="
    print query
    uri = prefix + query + suffix
    print uri
    page = requests.get(uri)
    tree = html.fromstring(page.text)
    # extract data
    try:
        news_nodes = tree.xpath('//div[@class="sn_r"]')
        urls = tree.xpath('//div[@class="newstitle"]/a/@href')
        for i in range(len(news_nodes)):
            print i
            hl_xpath = '//div[@class="sn_r"][' + \
                str(i + 1) + ']/div[@class="newstitle"]/a//text()'
            headline = tree.xpath(hl_xpath)
            print headline, ' ## ', urls[i]
    except:
        print 'No relevant data'


if __name__ == "__main__":
    main(sys.argv[1:])
