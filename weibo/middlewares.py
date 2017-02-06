# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random
from cookies import cookies
from useragents import agents


class WeiboUaMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    def process_request(self, request, spider):
        # This method is used by Scrapy to create your spiders.
        ua = random.choice(agents)
        request.headers["User-Agent"] = ua
        request.headers["Upgrade-Insecure-Requests"] = 1

class WeiboCookieMiddleware(object):
    # change cookie

    def process_request(self, request, spider):
        cookie = random.choice(cookies)
        request.cookies = cookie
