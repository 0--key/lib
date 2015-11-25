import spynner
import urllib2, os
from urlparse import urljoin
"""

"""
start_pages = ["http://www.impactguns.com/handguns.aspx", "http://www.impactguns.com/shotguns.aspx", "http://www.impactguns.com/rifles.aspx"]
items = []
url_prefix = "http://www.impactguns.com/"
browser = spynner.Browser()
for first_page in start_pages:
    browser.load(first_page)
    #let's extract pagination range:
    pagination = int(browser.html.split('<div class="TopPaging">')[1].split('</select>')[0].split('</option>')[-2].split('>')[-1])
    for k in range(pagination):
        chunks = browser.html.split('<div class="DetailLink">')
        # put a top of the page to /dev/null:
        chunks = chunks[1:]
        # let's cut a tail:
        pure_items = []
        for i in chunks:
            pure_items.append(i.split('<div style="clear: both;">')[0])
        for j in pure_items:
            model = j.split('.aspx">')[1].split('</a>')[0] # model
            url = urljoin(url_prefix, j.split('class="DetailLink" href="')[1].split('">')[0]) # url
            man_source = urllib2.urlopen(url)
            manufacturer = man_source.read()
            try:
                manufacturer.split("MANUFACTURER NO:")[1].split('</span>')[0]
            except IndexError:
                manufacturer_no = "Unknown"
            else:
                manufacturer_no = manufacturer.split("MANUFACTURER NO:")[1].split('</span>')[0]
            price = j.split('<span class="Price">')[-1].split('</span>')[0] # price
            if "</a>" in price:
                price = j.split('span class="SalePrice">')[1].split('</span></span>')[0]
            items.append(model + " " + url + " " + price + " " +  manufacturer_no + "\n")
            print model, url, price, manufacturer_no

        browser.runjs("__doPostBack('ctl00$ctl00$MainContent$uxCategory$uxCategoryProductList$TopNextLink','')")
        browser.wait_load()


f = open('OutputGuns.txt', 'w')
f.writelines(items)
browser.close()
