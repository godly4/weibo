# -*- coding: utf-8 -*-
import re
import json
import time
import random
import scrapy
import redis
import logging
import requests
from weibo.items import WeiboItem
from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.log import configure_logging
from requests.exceptions import ConnectTimeout, ReadTimeout

configure_logging(install_root_handler=False)
#定义了logging的些属性
logging.basicConfig(
    filename='scrapy.log',
    format='%(levelname)s: %(levelname)s: %(message)s',
    level=logging.INFO
)
#运行时追加模式
logger = logging.getLogger('SimilarFace')

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redisClient = redis.StrictRedis(connection_pool=pool)

def getIp(urlOri):
    times = 0
    while True:
        if times > 3:
            return None,"" 
        count = redisClient.llen("PROXY_IPS")
        index = random.randint(0, count)
        proxyIp = redisClient.lindex("PROXY_IPS", index)
        proxies = {'http': 'http://{0}'.format(proxyIp)}
        try:
            reqUrl = "http://duanwangzhihuanyuan.51240.com/web_system/51240_com_www/system/file/duanwangzhihuanyuan/get/"
            data = {
                'turl' : 't.cn/{0}'.format(urlOri),
            }
            r = requests.post(reqUrl, data, proxies=proxies, timeout=3)
            if r.status_code == 200:
                return proxies['http'], r.text
        except ConnectTimeout:
            logger.info("[[connect timeout wait for 3s to try again]]" + proxies['http']+" "+urlOri)
        except ReadTimeout:
            times += 1
            logger.info("[[read timeout {0} times for {1}]]".format(times, urlOri))
        except Exception as e:
            logger.info("[[proxy error wait for 3s to try again]]" + proxies['http']+" "+str(e.message)+" "+urlOri)
            #redisClient.lrem("PROXY_IPS", 0, proxyIp)

class WeibocrawlerSpider(CrawlSpider):
    name = "weibocrawler6"

    def transfer(self, urlOri):
        logger.info("[[get]] ori url "+urlOri)
        proxy, content = getIp(urlOri)
        urls = re.findall("http://weibo.com/p/(.*?)\"",content)
        if urls:
            poiid = urls[0][6:]
            url = "http://place.weibo.com/h5map_body.php?poiid={0}".format(poiid)
            logger.info("[[done]] {0}->{1}".format(urlOri, url))
            return proxy, url
        else:
            logger.info("[[transer error]] "+urlOri)
        return None,None

    def start_requests(self):
        urlDict = {}
        blockDict = {}
        with open("blockUrl.csv", "r") as f:
            line = f.readline().strip()
            while line:
                lineSplit = line.split(',')
                blockDict[lineSplit[0]] = "block"
                line = f.readline().strip()

        logger.info(blockDict)
        with open("locationInfo.csv", "r") as f:
            line = f.readline()
            while line:
                lineSplit = line.split(',')
                urlDict[lineSplit[0]] = lineSplit[1]
                line = f.readline()

        for date in range(6,7):
            with open("location/weibo.location.2016-10-0{0}".format(date),"r") as f:
                lineNum = 1
                line = f.readline().strip()
                while line:
                    logger.info("{0}-{1}".format(date, lineNum))
                    lineSplit = line.split('\t')
                    urls = re.findall("data-url=\"(.*?)\"", lineSplit[9])
                    if not urls:
                        urls = re.findall("_btn_c6\" href=\"http://t.cn/(.*?)\"", lineSplit[9])
                    for url in urls:
                        url = url.replace('http://t.cn/','').strip()
                        if url in urlDict:
                            logger.info("[[exist url]] "+url)
                        elif len(url)!=7:
                            logger.info("[[error url]] "+url)
                        elif url in blockDict:
                            logger.info("[[block url]] "+url)
                        else:
                            proxy, newUrl = self.transfer(url)
                            if newUrl:
                                urlDict[url] = newUrl
                                yield Request(url=newUrl, meta={"info":urlDict,"key":url,"proxy":proxy}, callback=self.parseWeibo)
                            else:
                                blockDict[url] = "block"
                                with open("blockUrl.csv", "a") as fb:                        
                                    fb.write("{0}\n".format(url))
                    lineNum += 1
                    line = f.readline().strip()

    def parseWeibo(self, response):
        #text = re.findall("poiinfo = (.*);", response.text)[0]
        center = re.findall("center = (.*);", response.text)[0]
        text = response.text
        
        urlDict = response.meta["info"]
        key = response.meta["key"]

        with open("locationInfo.csv", "a") as fw:
            #data = json.loads(text)
            pos  = json.loads(center)
            logger.info('{0}'.format(pos))
            checkin_user = -1
            checkin = -1
            photo = -1
            if re.findall("checkin_user_num|checkin_num|photo_num", text):
                checkin_user = re.findall("checkin_user_num\":(\d+)",text)[0]
                checkin      = re.findall("checkin_num\":(\d+)",text)[0]
                photo        = re.findall("photo_num\":(\d+)",text)[0]
            else:
                logger.info("[[error]] "+text)
            fw.write("{0},{1},{2},{3},{4},{5},{6}\n".format(key, urlDict[key], pos[0], pos[1], \
                        checkin_user, checkin, photo))
