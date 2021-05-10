# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from itemadapter import ItemAdapter
import re
import pymongo

class BookparserPipeline(object):

    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.client["gb_data_mining"]

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if spider.name == "labirint":
            clear_price = self.labirint_price(adapter["price"])

            if len(clear_price) == 1:
                adapter.update({"price": clear_price[0]})
            else:
                adapter.update({"price": clear_price[1]})
                adapter.update({"old_price": clear_price[0]})

        elif spider.name == "book24":
            adapter.update({"name": self.book24_name(adapter["name"])})
            adapter.update({"price": self.book24_price(adapter["price"])})

            if any(map(str.isdigit, item["old_price"])):
                adapter.update({"old_price": self.book24_price(adapter["old_price"])})
            else:
                del item["old_price"]

        self.db[spider.name].update_one({"name": item["name"]}, {"$set": item}, upsert=True)

        return item

    def labirint_price(self, price: list):
        price_lst = [x for x in price if x.isdigit()]
        return price_lst

    def book24_price(self, price: str):
        cleared_price = re.findall('\d+', price)
        return ''.join(cleared_price)

    def book24_name(self, name: str):
        return name.strip()