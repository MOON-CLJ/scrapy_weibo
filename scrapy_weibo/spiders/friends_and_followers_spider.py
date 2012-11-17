import redis
import math
import simplejson as json
from scrapy.spider import BaseSpider
from scrapy_weibo.items import WeiboItem, UserItem
from scrapy import log
from scrapy.conf import settings
from scrapy.exceptions import CloseSpider
from scrapy.http import Request


REDIS_HOST = 'localhost'
REDIS_PORT = 6379
UIDS_SET = '{spider}:uids'
FOLLOWERS_URL = 'https://api.weibo.com/2/friendships/followers.json?uid={uid}&cursor={cursor}&count=200'
FRIENDS_URL = 'https://api.weibo.com/2/friendships/friends.json?uid={uid}&cursor={cursor}&count=200'


class FriendsAndFollowersSpider(BaseSpider):
    name = 'friends_and_followers'
    r = None

    def start_requests(self):
        uids = self.prepare()

        for uid in uids:
            request = Request(FOLLOWERS_URL.format(uid=uid), headers=None,
                              callback=self.parse_follower)

            yield request

            request = Request(FRIENDS_URL.format(uid=uid), headers=None,
                              callback=self.parse_friend)

            yield request

    def parse_follower(self, response):
        return

    def parse_friend(self, response):
        return

    def prepare(self):
        host = settings.get("REDIS_HOST", REDIS_HOST)
        port = settings.get("REDIS_PORT", REDIS_PORT)
        uids_set = UIDS_SET.format(spider=self.name)

        self.r = redis.Redis(host, port)

        log.msg("load uids from {uids_set}".format(uids_set=uids_set), level=log.INFO)
        uids = self.r.smembers(uids_set)
        if len(uids) == 0:
            log.msg("{spider}: NO USER IDS TO LOAD".format(spider=self.name), level=log.WARNING)

        return uids
