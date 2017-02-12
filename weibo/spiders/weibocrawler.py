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
    allowed_domains = ["weibo.com"]
    start_urls = ['http://weibo.com/p/100101B2094654D06AA5F8429D?containerid=100101B2094654D06AA5F8429D&sourceType=weixin&featurecode=20000180&oid=4071365839752392&luicode=10000011&lfid=100101B2094654D06AA5F8429D#1486380822494']

    rules = [
        Rule(
            LinkExtractor(
                restrict_xpaths='//a[contains(@class,"next") and (@bpfilter="page")]'
            ), callback="parseWeibo", follow=True,
        )
    ]

    def parse_start_url(self, response):
        with open("/tmp/tmpres.html","w") as f:
            f.write(response.text.encode('utf8'))
        print response.xpath("//div")
        self.parseWeibo(response)

    def parseWeibo(self, response):
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
