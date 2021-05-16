# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import os
from urllib.parse import urlparse
import pymongo

class Lesson7ImagesPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None, *, item):
        if item["photos"]:
            return f'{item["name"]}/{os.path.basename(urlparse(request.url).path)}'

    def get_media_requests(self, item, info):
        if item["photos"]:
            try:
                for url in item["photos"]:
                    yield scrapy.Request(url)
            except Exception as err:
                print(err)

    def item_completed(self, results, item, info):
        if results:
            item["photos"] = [itm[1]["path"] for itm in results if itm[0]]
        return item


class Lesson7Pipeline:

    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.client["gb_data_mining"]

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        adapter["parameters"] = self.clean_params(adapter["parameters"])
        self.db[spider.name].update_one({"name": item["name"]}, {"$set": item}, upsert=True)
        return item

    def clean_params(self, params:dict):
        clean_dict = {}
        for key, value in params.items():
            clean_dict[key] = value.replace('\n', '').strip()
        return clean_dict

