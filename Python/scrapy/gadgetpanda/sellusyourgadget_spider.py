import os
import csv
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from product_spiders.fuzzywuzzy import process

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class SellUsYourGadgetSpider(BaseSpider):
    name = 'sellusyourgadget.co.uk'
    allowed_domains = ['sellusyourgadget.co.uk']
    start_urls = ['http://sellusyourgadget.co.uk/index.php/home/myProduct']

    def __init__(self, *args, **kwargs):
        super(SellUsYourGadgetSpider, self).__init__(*args, **kwargs)
        csv_file = csv.reader(open(os.path.join(HERE, 'sellusyourgadget_products.csv')))
        self.products =[row[0] for row in csv_file]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        product_ids = hxs.select('//*[@id="product"]/option/@value').extract()
        for id in product_ids:
            url = 'http://sellusyourgadget.co.uk/index.php/home/getSubProducts/%s'
            yield Request(url % id, callback=self.parse_subproducts, meta={'id': id})

    def parse_subproducts(self, response):
        hxs = HtmlXPathSelector(response)
        #Fix for the HTML code.
        html = hxs.extract().replace('<br></h3>','').\
                             replace('<h3','<div class="item"').\
                             replace('</p>\n                                            <div','</p></div>\n    <div').\
                             replace('<input type="radio"', '<div class="hd" ').\
                             replace('checked>','>').\
                             replace('</p></div>','</div></p></div>').\
                             replace('</p>\n', '</div></p>\n')

        products_hxs = HtmlXPathSelector(text=html)
        products = products_hxs.select('//div[@class="item"]')
        for product in products:
            sub_products = product.select('div[@class="hd"]')
            if sub_products:
                for sub_product in sub_products:
                    value = sub_product.select('./@value').extract()[0]
                    hd = sub_product.select('./text()').extract()[0]
                    name = ' '.join((product.select('p/text()').extract()[0], hd))
                    extracted = process.extractOne(name, self.products)
                    try:
                        if extracted[1]>=98:                    
                            url = 'http://sellusyourgadget.co.uk/index.php/home/getConditions/%s'
                            yield Request(url % value.split(':')[0], callback=self.parse_options, 
                                          meta={'id':response.meta['id'],
                                                'name': name, 
                                                'memoryR':value,
                                                'memory':value})
                    except TypeError:
                        return
            else:
                name = product.select('p/text()').extract()[0]
                extracted = process.extractOne(name, self.products)
                try:
                    if extracted[1]>=98:
                        value = product.select('p/input/@value').extract()[0]
                        url = 'http://sellusyourgadget.co.uk/index.php/home/getConditions/%s'
                        yield Request(url % value.split(':')[0], callback=self.parse_options, 
                                      meta={'id':response.meta['id'],
                                            'name':name, 
                                            'memoryR':value,
                                            'memory':value})
                except TypeError:
                    return 

    def parse_options(self, response):
        '''Gets the percentages to be subtracted to the initial price.
        '''
        try:
            hxs = HtmlXPathSelector(response)
            percentages = hxs.select('//input[@name="conditionR"]/@value').extract()
            grade_values = dict(zip(['Grade A','Grade B', 'Grade C', 
                                     'Grade D', 'Grade E'], percentages))
            for grade, percentage in grade_values.iteritems():
                yield FormRequest('http://sellusyourgadget.co.uk/index.php/home/getQuote',
                                   method='POST', 
                                   formdata={'product':response.meta['id'], 
                                             'memoryR':response.meta['memoryR'], 
                                             'conditionR':percentage, 
                                             'condition':percentage,
                                             'memory':response.meta['memory'], 
                                             'tick1':'0',
                                             'tick2':'0', 
                                             'tick3':'0', 
                                             'tick4':'0',
                                             'price':''}, 
                                             callback=self.parse_product, 
                                             meta={'name': ' '.join((response.meta['name'], grade))})
        except TypeError:
            return

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        loader = ProductLoader(item=Product(), response=response)
        loader.add_value('name', response.meta['name'])
        loader.add_xpath('price', '//*[@id="price-text"]/span/text()')
        yield loader.load_item()
        
