import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest
from product_spiders.items import ProductLoader, Product

class pretavoirSpider(BaseSpider):

    name = "pretavoir.co.uk"
    allowed_domains = ["www.pretavoir.co.uk"]
    start_urls = (
            'http://www.pretavoir.co.uk/bvlgari-glasses-c-26_49.html',
            'http://www.pretavoir.co.uk/carrera-sunglasses-c-1816_1817.html',
            'http://www.pretavoir.co.uk/cartier-glasses-c-3118_3125.html',
            'http://www.pretavoir.co.uk/dg-glasses-c-1700_1701.html',
            'http://www.pretavoir.co.uk/dior-glasses-c-29_91.html',
            'http://www.pretavoir.co.uk/dolce-and-gabbana-glasses-c-30_112.html',
            'http://www.pretavoir.co.uk/emporio-armani-glasses-c-2367_2457.html',
            'http://www.pretavoir.co.uk/giorgio-armani-glasses-c-1882_1987.html',
            'http://www.pretavoir.co.uk/gucci-glasses-c-32_92.html',
            'http://www.pretavoir.co.uk/hugo-glasses-c-2938_2951.html',
            'http://www.pretavoir.co.uk/hugo-boss-glasses-c-2981_2982.html',
            'http://www.pretavoir.co.uk/jimmy-choo-glasses-c-3270_3271.html',
            'http://www.pretavoir.co.uk/marc-by-marc-jacobs-glasses-c-1526_1571.html',
            'http://www.pretavoir.co.uk/marc-jacobs-glasses-c-35_115.html',
            'http://www.pretavoir.co.uk/oakley-glasses-c-75_79.html',
            'http://www.pretavoir.co.uk/persol-glasses-c-1334_1335.html',
            'http://www.pretavoir.co.uk/prada-glasses-c-68_99.html',
            'http://www.pretavoir.co.uk/prada-sports-glasses-c-2283_2313.html',
            'http://www.pretavoir.co.uk/ray-ban-glasses-c-76_106.html',
            'http://www.pretavoir.co.uk/tag-heuer-glasses-c-2770_2792.html',
            'http://www.pretavoir.co.uk/tiffany-co-glasses-c-123_124.html',
            'http://www.pretavoir.co.uk/glasses-c-5798_5800.html',
            'http://www.pretavoir.co.uk/ralph-lauren-glasses-c-5369_5370.html',
            'http://www.pretavoir.co.uk/adidas-goggles-c-3983_3985.html',
            'http://www.pretavoir.co.uk/adidas-sunglasses-c-3983_3984.html',
            'http://www.pretavoir.co.uk/alain-mikli-glasses-c-3526_3527.html',
            'http://www.pretavoir.co.uk/bolle-goggles-c-5801_5805.html',
            'http://www.pretavoir.co.uk/bolle-ski-helmets-c-5801_5807.html',
            'http://www.pretavoir.co.uk/bolle-sunglasses-c-5801_5806.html',
            'http://www.pretavoir.co.uk/boss-orange-glasses-c-5163_5165.html',
            'http://www.pretavoir.co.uk/boss-orange-sunglasses-c-5163_5164.html',
            'http://www.pretavoir.co.uk/bugatti-glasses-c-2097_2229.html',
            'http://www.pretavoir.co.uk/bvlgari-sunglasses-c-26_89.html',
            'http://www.pretavoir.co.uk/carrera-eyeglasses-c-1816_5148.html',
            'http://www.pretavoir.co.uk/cartier-sunglasses-c-3118_3124.html',
            'http://www.pretavoir.co.uk/chanel-sunglasses-c-28_52.html',
            'http://www.pretavoir.co.uk/chanel-glasses-c-28_90.html',
            'http://www.pretavoir.co.uk/dg-sunglasses-c-1700_1702.html',
            'http://www.pretavoir.co.uk/dior-sunglasses-c-29_53.html',
            'http://www.pretavoir.co.uk/dolce-and-gabbana-sunglasses-c-30_54.html',
            'http://www.pretavoir.co.uk/emporio-armani-sunglasses-c-2367_2368.html',
            'http://www.pretavoir.co.uk/giorgio-armani-sunglasses-c-1882_1883.html',
            'http://www.pretavoir.co.uk/givenchy-sunglasses-c-3149_3195.html',
            'http://www.pretavoir.co.uk/givenchy-glasses-c-3149_3150.html',
            'http://www.pretavoir.co.uk/gucci-sunglasses-c-32_57.html',
            'http://www.pretavoir.co.uk/hugo-sunglasses-c-2938_2939.html',
            'http://www.pretavoir.co.uk/hugo-boss-sunglasses-c-2981_3055.html',
            'http://www.pretavoir.co.uk/ic-berlin-glasses-c-3417_3418.html',
            'http://www.pretavoir.co.uk/ic-berlin-sunglasses-c-3417_3419.html',
            'http://www.pretavoir.co.uk/jimmy-choo-sunglasses-c-3270_3281.html',
            'http://www.pretavoir.co.uk/lacoste-glasses-c-4032_4033.html',
            'http://www.pretavoir.co.uk/lacoste-sunglasses-c-4032_4034.html',
            'http://www.pretavoir.co.uk/marc-by-marc-jacobs-sunglasses-c-1526_1527.html',
            'http://www.pretavoir.co.uk/marc-jacobs-sunglasses-c-35_59.html',
            'http://www.pretavoir.co.uk/miu-miu-glasses-c-1364_1365.html',
            'http://www.pretavoir.co.uk/miu-miu-sunglasses-c-1364_1366.html',
            'http://www.pretavoir.co.uk/nike-glasses-c-4134_4136.html',
            'http://www.pretavoir.co.uk/nike-sunglasses-c-4134_4135.html',
            'http://www.pretavoir.co.uk/oakley-glasses-c-75_79.html',
            'http://www.pretavoir.co.uk/oakley-goggles-c-75_3809.html',
            'http://www.pretavoir.co.uk/oakley-mens-active-c-75_3397.html',
            'http://www.pretavoir.co.uk/oakley-mens-lifestyle-c-75_3398.html',
            'http://www.pretavoir.co.uk/oakley-mens-sports-c-75_3396.html',
            'http://www.pretavoir.co.uk/oakley-sunglasses-c-75_80.html',
            'http://www.pretavoir.co.uk/oakley-women-sports-c-75_3399.html',
            'http://www.pretavoir.co.uk/oakley-womens-active-c-75_3400.html',
            'http://www.pretavoir.co.uk/oakley-womens-lifestyle-c-75_3402.html',
            'http://www.pretavoir.co.uk/oliver-peoples-glasses-c-3301_3331.html',
            'http://www.pretavoir.co.uk/oliver-peoples-sunglasses-c-3301_3302.html',
            'http://www.pretavoir.co.uk/oxydo-glasses-c-5208_5209.html',
            'http://www.pretavoir.co.uk/paul-smith-glasses-c-3222_3223.html',
            'http://www.pretavoir.co.uk/paul-smith-sunglasses-c-3222_3250.html',
            'http://www.pretavoir.co.uk/persol-sunglasses-c-1334_1336.html',
            'http://www.pretavoir.co.uk/police-glasses-c-2666_2667.html',
            'http://www.pretavoir.co.uk/police-sunglasses-c-2666_2709.html',
            'http://www.pretavoir.co.uk/polo-glasses-c-5516_5517.html',
            'http://www.pretavoir.co.uk/polo-sunglasses-c-5516_5518.html',
            'http://www.pretavoir.co.uk/porsche-glasses-c-2864_2866.html',
            'http://www.pretavoir.co.uk/porsche-sunglasses-c-2864_2899.html',
            'http://www.pretavoir.co.uk/prada-sunglasses-c-68_100.html',
            'http://www.pretavoir.co.uk/prada-sport-sunglasses-c-2283_2284.html',
            'http://www.pretavoir.co.uk/prada-sports-glasses-c-2283_2313.html',
            'http://www.pretavoir.co.uk/ralph-lauren-glasses-c-5369_5370.html',
            'http://www.pretavoir.co.uk/ralph-lauren-sunglasses-c-5369_5371.html',
            'http://www.pretavoir.co.uk/ray-ban-sunglasses-c-76_101.html',
            'http://www.pretavoir.co.uk/starck-glasses-c-3553_3598.html',
            'http://www.pretavoir.co.uk/tag-heuer-sunglasses-c-2770_2771.html',
            'http://www.pretavoir.co.uk/tiffany-co-sunglasses-c-123_125.html',
            'http://www.pretavoir.co.uk/tods-glasses-c-5798_5800.html',
            'http://www.pretavoir.co.uk/tods-sunglasses-c-5798_5799.html',
            'http://www.pretavoir.co.uk/tom-ford-glasses-c-24_103.html',
            'http://www.pretavoir.co.uk/tom-ford-sunglasses-c-24_65.html',
            'http://www.pretavoir.co.uk/versace-glasses-c-69_105.html',
            'http://www.pretavoir.co.uk/versace-sunglasses-c-69_104.html',
            'http://www.pretavoir.co.uk/versus-glasses-c-1331_1332.html',
            'http://www.pretavoir.co.uk/versus-sunglasses-c-1331_1333.html',
            'http://www.pretavoir.co.uk/vivienne-westwood-sunglasses-c-2455_2456.html',
        )
    
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//td[@class='smallText']")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(item, callback=self.parse_item)
             
            
    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        name = hxs.select("//td[@class='pushright']/h1[@class='cat']/span/text()").re(r'^(.*).*\(.*\)')
        url = response.url
        price = hxs.select("///td[@class='pushright']/h1[@class='cat']/span/text()").re(r'\xa3(.*)\)')

        l = ProductLoader(item=Product(), response=response)
        l.add_value('name', name)        
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()

        content = hxs.select("//td[@class='smallText']//td[@class='thumbcontent']")
        items = content.select(".//a/@href").extract()

        for item in items:
            yield Request(item, callback=self.parse_item)
