# -*- coding: utf-8 -*-
import re
import scrapy
import redis
import logging
import requests
from weibo.items import WeiboItem
from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.log import configure_logging

configure_logging(install_root_handler=False)
#定义了logging的些属性
logging.basicConfig(
    filename='scrapy.log',
    format='%(levelname)s: %(levelname)s: %(message)s',
    level=logging.INFO
)
#运行时追加模式
logger = logging.getLogger('SimilarFace')

class WeibocrawlerSpider(CrawlSpider):
    name = "weibocrawler"
    start_urls = ['http://m.weibo.cn/p/100101B2094654D06AA5F8429D/']

    def parse(self, response):
        cards = response.xpath("//div[@class='card-main']")
        print cards,'*'*8, response
        logger.info("lens is {0}".format(len(cards)))
        details = response.xpath("//div[@class='WB_detail']")
        for detail in details:
            weiboItem = WeiboItem()
            uidInfo = detail.xpath("div[@class='WB_info']/a/@usercard").extract_first()
            uid = re.findall('id=(\d+)',uidInfo)
            if len(uid) == 1:
                weiboItem["uid"] = uid[0]
            timeInfo = detail.xpath("div[contains(@class,'WB_from')]/a/@title").extract_first()
            weiboItem["time"] = timeInfo
            weiboItem["lat"] = 36
            weiboItem["lon"] = 120
            logger.info("Get twitter at {0} from {1}".format(timeInfo, weiboItem["uid"]))
            yield weiboItem
