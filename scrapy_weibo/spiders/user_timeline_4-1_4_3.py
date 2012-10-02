import redis
import simplejson as json
from scrapy.spider import BaseSpider
from scrapy_weibo.items import WeiboItem, UserItem
from scrapy import log
from scrapy.conf import settings
from scrapy.exceptions import CloseSpider
from scrapy.http import Request


# weibo apis default extras config
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
UIDS_SET = '{spider}:uids'
BASE_URL = 'https://api.weibo.com/2/statuses/user_timeline.json?uid={uid}&page={page}&since_id={since_id}&max_id={max_id}&count=100'
LIMIT_URL = 'https://api.weibo.com/2/account/rate_limit_status.json?access_token={access_token}'


class UserTimelineApril(BaseSpider):
    name = "user_timeline_april"
    r = None
    since_id = 3421438975589423
    max_id = 3438780670993204

    def start_requests(self):
        uids = self.prepare()

        for uid in uids:
            request = Request(BASE_URL.format(uid=uid, page=1,
                              since_id=self.since_id, max_id=self.max_id), headers=None,
                              callback=self.parse_next)

            request.meta['page'] = 1
            request.meta['retry'] = 0
            request.meta['uid'] = uid
            yield request

    def parse_next(self, response):
        resp = json.loads(response.body)
        page = response.meta['page']
        retry = response.meta['retry']
        uid = response.meta['uid']

        if "error_code" in resp and resp["error_code"] in [21314, 21315, 21316, 21317]:
            raise CloseSpider('ERROR: TOKEN NOT VALID')

        if 'statuses' in resp and resp['statuses'] == []:
            retry += 1
            if retry > 2:
                return
        else:
            for status in resp["statuses"]:
                try:
                    weibo = WeiboItem()
                    user = UserItem()

                    weibo['created_at'] = status["created_at"]
                    weibo['id'] = status['id']
                    weibo['text'] = status['text']
                    weibo['source'] = status['source']
                    weibo['comments_count'] = status['comments_count']

                    user['uid'] = status['user']['id']
                    user['name'] = status['user']['name']
                    user['gender'] = status['user']['gender']
                    user['location'] = status['user']['location']
                    user['verified'] = status['user']['verified']

                    weibo['user'] = user

                    if 'retweeted_status' in status:
                        if 'deleted' in status['retweeted_status']:
                            continue
                        retweeted_user = UserItem()
                        retweeted_user['name'] = status['retweeted_status']['user']['name']

                        weibo['retweeted_status'] = WeiboItem()
                        weibo['retweeted_status']['user'] = retweeted_user

                    yield weibo
                except KeyError:
                    continue

            page += 1
            retry = 0

        request = Request(BASE_URL.format(uid=uid, page=page,
                          since_id=self.since_id, max_id=self.max_id),
                          headers=None, callback=self.parse_next, dont_filter=True)

        request.meta['page'] = page
        request.meta['retry'] = retry
        request.meta['uid'] = uid

        yield request

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
