#coding:utf-8
import re
import redis
import scrapy
import requests
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redisClient = redis.StrictRedis(connection_pool=pool)

def checkIp(ipList):
    availables = []
    for ipInfo in ipList:
        proxyIp = ipInfo.strip().split('@')[0]
        if proxyIp:
            proxies = {'http': 'http://{0}'.format(proxyIp)}
            try:
                r = requests.get("http://icanhazip.com/", timeout=3, proxies=proxies)
                if r.status_code == 200:
                    if r.text.strip() == proxyIp.split(':')[0] and (not proxyIp in redisClient.lrange("PROXY_IPS",0,-1)):
                        print proxyIp, r.text.strip() == proxyIp.split(':')[0]
                        redisClient.rpush('PROXY_IPS',proxyIp)
            except:
                pass

class ProxySpider(CrawlSpider):
    name = "proxy"
    start_urls = ['http://www.youdaili.net/Daili/http/']
    
    rules = (
        Rule(LinkExtractor(restrict_xpaths=('//div[@class="chunlist"]','//div[@class="pagebreak"]')),\
                callback='parse_ips',follow=True),
    )
    
    def parse_ips(self, response):
        for ipInfo in response.xpath('//div[@class="content"]'):
            if not ipInfo.xpath('p/span'):
                checkIp(ipInfo.xpath('p/text()').extract())
            else:
                checkIp(ipInfo.xpath('p/span/text()').extract())
