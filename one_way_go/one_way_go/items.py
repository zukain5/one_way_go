# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OneWayGoItem(scrapy.Item):
    departure_shop = scrapy.Field()
    arrival_shop = scrapy.Field()
    car_info = scrapy.Field()
    car_capacity = scrapy.Field()
    departure_since = scrapy.Field()
    departure_until = scrapy.Field()
    reserve_shop = scrapy.Field()
    reserve_number = scrapy.Field()
    is_available = scrapy.Field()
