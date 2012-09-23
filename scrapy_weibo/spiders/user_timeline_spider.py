import redis
from scrapy.spider import BaseSpider
from scrapy import log
from scrapy.settings import Settings
from scrapy.exceptions import CloseSpider
from scrapy.http import Request


# weibo apis default extras config
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
UIDS_SET = '{spider}:uids'
TOKENS_SET = '{spider}:tokens'
BASE_URL = 'https://api.weibo.com/2/statuses/user_timeline.json?uid={uid}&page={page}&count=100'


class UserTimelineSpider(BaseSpider):
    name = "user_timeline"
    allowed_domains = ["api.weibo.com"]

    def start_requests(self):
        uids, token = self.load_uids_token()
        for uid in uids:
            for page in (1, 2):
                yield Request(BASE_URL.format(uid=uid, page=page),
                              headers={'Authorization': 'OAuth2 %s' % token})

    def parse(self, response):
        pass

    def load_uids_token(self):
        settings = Settings()
        host = settings.get("REDIS_HOST", REDIS_HOST)
        port = settings.get("REDIS_PORT", REDIS_PORT)
        uids_set = UIDS_SET.format(spider=self.name)
        tokens_set = TOKENS_SET.format(spider=self.name)

        r = redis.Redis(host, port)
        log.msg("load uids from {uids_set}".format(uids_set=uids_set), level=log.INFO)
        uids = r.smembers(uids_set)
        token = r.spop(tokens_set)
        if len(uids) == 0:
            log.msg("{spider}: NO USER IDS TO LOAD".format(spider=self.name), level=log.WARNING)
        if token is None:
            raise CloseSpider('NO TOKEN, ARE YOU KIDDING ME')

        return uids, token
