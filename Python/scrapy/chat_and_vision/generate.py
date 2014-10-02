"""
Used to generate spiders from skype.py spider
"""
from __future__ import with_statement

import re

sites = {
    'SkypeFrMa': 'http://shop.skype.com/intl/fr-ma',
    'SkypeEnAu': 'http://shop.skype.com/intl/en-au',
    'SkypeEnIl': 'http://shop.skype.com/intl/en-il',
    'SkypeEnCy': 'http://shop.skype.com/intl/en-cy',
    'SkypeEnHk': 'http://shop.skype.com/intl/en-hk',
    'SkypeEnAe': 'http://shop.skype.com/intl/en-ae',
    'SkypeDe': 'http://shop.skype.com/intl/de',
    'SkypeEnIe': 'http://shop.skype.com/intl/en-ie',
    'SkypeEnId': 'http://shop.skype.com/intl/en-id',
    'SkypeFrCh': 'http://shop.skype.com/intl/fr-ch',
    'SkypeEnFi': 'http://shop.skype.com/intl/en-fi',
    'SkypeEnNz': 'http://shop.skype.com/intl/en-nz',
    'SkypeEnLt': 'http://shop.skype.com/intl/en-lt',
    'SkypeEnGr': 'http://shop.skype.com/intl/en-gr',
    'SkypeEnBg': 'http://shop.skype.com/intl/en-bg',
    'SkypeFrLu': 'http://shop.skype.com/intl/fr-lu',
    'SkypeEnHu': 'http://shop.skype.com/intl/en-hu',
    'SkypeEnIn': 'http://shop.skype.com/intl/en-in',
    'SkypeEnZa': 'http://shop.skype.com/intl/en-za',
    'SkypeEnCa': 'http://shop.skype.com/intl/en-ca',
    'SkypeEnPh': 'http://shop.skype.com/intl/en-ph',
    'SkypeEnEe': 'http://shop.skype.com/intl/en-ee',
    'SkypeEnTh': 'http://shop.skype.com/intl/en-th',
    'SkypeEnCz': 'http://shop.skype.com/intl/en-cz',
    'SkypeEnSi': 'http://shop.skype.com/intl/en-si',
    'SkypeEnTn': 'http://shop.skype.com/intl/en-tn',
    'SkypeEnQa': 'http://shop.skype.com/intl/en-qa',
    'SkypeFrBe': 'http://shop.skype.com/intl/fr-be',
    'SkypeEnLv': 'http://shop.skype.com/intl/en-lv',
    'SkypeEnSg': 'http://shop.skype.com/intl/en-sg',
    'SkypeDeAt': 'http://shop.skype.com/intl/de-at',
    'SkypeEnSa': 'http://shop.skype.com/intl/en-sa',
    'SkypeEnRo': 'http://shop.skype.com/intl/en-ro',
    'SkypeFr': 'http://shop.skype.com/intl/fr',
    'SkypeEnRs': 'http://shop.skype.com/intl/en-rs',
    'SkypeEnGb': 'http://shop.skype.com/intl/en-gb',
    'SkypeEnOm': 'http://shop.skype.com/intl/en-om',
    'SkypeEnHr': 'http://shop.skype.com/intl/en-hr',
    'SkypeEnMy': 'http://shop.skype.com/intl/en-my',
    'SkypeEnTw': 'http://shop.skype.com/intl/en-tw'
}

if __name__ == "__main__":
    with open("skype.py", 'r') as handle:
        template = handle.read()

    for name, site_name in sites.items():
        code = re.sub("name = '[^']*'", "name = '%s'" % name, template)
        code = re.sub("class SkypeSpider", "class %sSpider" % name, code)
        code = re.sub("site_name = '[^']*'", "site_name = '%s'" % site_name, code)

        filename = name.lower() + ".py"
        with open(filename, 'w+') as handle:
            handle.write(code)