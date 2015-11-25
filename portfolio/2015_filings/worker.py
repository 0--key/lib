import urllib
import requests
import redis
import lxml.html
import time


from settings import R_HOST, R_PORT


class FilingItem():

    def __init__(self):
        self.company = ''
        self.pub_time = ''
        self.sec_form_type = ''
        self.document = ''

    def __str__(self):
        return "%s || %s || %s || %s" % (
            self.company, self.pub_time,
            self.sec_form_type,
            self.document
            )

    def generate_key(self):
        """Produce an unique key for Redis"""
        return "_".join(self.pub_time) + '__' + self.company

    def insert(self, key):
        """Put new filing into Redis"""
        r = redis.StrictRedis(host=R_HOST, port=R_PORT, db=0)
        r.hmset(key, {
            'company': self.company, 'pub_time': self.pub_time,
            'sec_form_type': self.sec_form_type,
            'document': self.document})


def main():
    """Parse data out from stock exchange page, detect the new
    entries and pass it out by HTTP POST"""
    last_inserted_key = ''
    for i in range(100):  # iterates it N times
        page_data = urllib.urlopen(
            'http://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent'
            )
        xmldata = lxml.html.parse(page_data).getroot()
        for i in range(2, 82, 2):
            prefix = "/html/body//table[2]/tr["
            path_to_name = prefix + str(i) + "]//a/text()"
            path_to_date = prefix + str(i+1) + "]/td[4]/text()"
            path_to_type = prefix + str(i+1) + "]/td[1]/text()"
            path_to_document = prefix + str(i+1) + "]/td[3]/text()"
            row = FilingItem()
            row.company = xmldata.xpath(path_to_name)[0]
            row.pub_time = xmldata.xpath(path_to_date)
            row.sec_form_type = xmldata.xpath(path_to_type)[0]
            row.document = xmldata.xpath(path_to_document)[0]
            key = row.generate_key()
            if last_inserted_key:
                if key == last_inserted_key:
                    break  # prevent unnecessary iteration
            else:
                last_inserted_key = key  # first item ever
            row.insert(key)
            # print row


if __name__ == "__main__":
    main()
