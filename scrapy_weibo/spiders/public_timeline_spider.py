import simplejson as json
from scrapy.spider import BaseSpider
from utils4scrapy.utils import resp2item
from scrapy.exceptions import DropItem


REDIS_HOST = 'localhost'
REDIS_PORT = 6379
BASE_URL = 'https://api.weibo.com/2/statuses/public_timeline.json?count=200'


class PublicTimelineSpider(BaseSpider):
    name = 'public_timeline'

    start_urls = [BASE_URL]

    def parse(self, response):
        if not (200 <= response.status < 300):
            return

        resp = json.loads(response.body)
        for status in resp['statuses']:
            try:
                user, weibo, retweeted_user = resp2item(status)
            except DropItem:
                continue

            print user, weibo
            yield user
            yield weibo
            if retweeted_user is not None:
                yield retweeted_user
