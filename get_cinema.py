import requests
from lxml import etree

headers={'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Mobile Safari/537.36',
         'Host':'m.maoyan.com'}
if __name__ == '__main__':
    city_dict={}
    with open('city.html','r') as f:
        selector=etree.HTML(f.read())
        city_list=selector.xpath("//div[@class='city-item']")
        for city in city_list:
            city_dict[city.xpath('string(./.)').strip()]=city.xpath('string(./@data-id)')
    print(city_dict)