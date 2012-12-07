import simplejson as json
from scrapy.spider import BaseSpider
from utils4scrapy.utils import resp2item_v2


BASE_URL = 'https://api.weibo.com/2/statuses/public_timeline.json?count=200'


class PublicTimelineSpider(BaseSpider):
    name = 'public_timeline'

    start_urls = [BASE_URL]

    def parse(self, response):
        # scrapy auto handle not 200-300 status
        resp = json.loads(response.body)
        for status in resp['statuses']:
            items = resp2item_v2(status)
            for item in items:
                yield item
