# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst, Compose


class Lesson7Item(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    parameters = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=Compose(lambda a: int(a[0].replace(" ", ""))), output_processor=TakeFirst())
    photos = scrapy.Field()

