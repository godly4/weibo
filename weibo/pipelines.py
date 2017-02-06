# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from items import WeiboItem


class WeiboPipeline(object):
    def __init__(self):
        mongoClient = pymongo.MongoClient("localhost", 27017)
        db = mongoClient["weibo_db"]
        self.Weibo = db["weibo"]

    def process_item(self, item, spider):
        if isinstance(item, WeiboItem):
            self.Weibo.insert(dict(item))
