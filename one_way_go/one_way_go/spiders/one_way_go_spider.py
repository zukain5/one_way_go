import re

import scrapy
from one_way_go.items import OneWayGoItem


class OneWayGoSpiderSpider(scrapy.Spider):
    name = 'one_way_go_spider'
    allowed_domains = ['cp.toyota.jp']
    start_urls = ['http://cp.toyota.jp/rentacar/']

    def parse(self, response):
        one_way_go_items = response.css('ul#service-items-shop-type-start')
        for one_way_go_item in one_way_go_items.css('div.service-item__body'):
            car_info = (one_way_go_item.css('div.service-item__info__car-type p::text')[1]
                        .extract().split('　'))
            car_condition = (one_way_go_item.css('div.service-item__info__condition p::text')[1]
                             .extract())
            departure_range = (one_way_go_item.css('div.service-item__info__date::text')[1]
                               .extract().strip())
            yield OneWayGoItem(
                departure_shop=(one_way_go_item.css('div.service-item__shop-start p::text')[2]
                                .extract().strip()),
                arrival_shop=(one_way_go_item.css('div.service-item__shop-return p::text')[2]
                              .extract().strip()),
                car=car_info[0],
                car_number=re.sub(r'\D', '', car_info[1]),
                car_capacity=re.sub(r'\D', '', car_condition),
                departure_since=departure_range.partition(' ～ ')[0],
                departure_until=departure_range.partition(' ～ ')[-1],
                reserve_shop='',    # TODO
                reserve_number='',  # TODO
                is_available=one_way_go_item.css('div.show-entry-end') == [],
            )
