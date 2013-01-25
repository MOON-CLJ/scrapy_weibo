import simplejson as json
from scrapy.spider import BaseSpider
from utils4scrapy.utils import resp2item_v2


BASE_URL = 'https://api.weibo.com/2/statuses/public_timeline.json?count=200'


class PublicTimelineSpider(BaseSpider):
    name = 'public_timeline'

    start_urls = [BASE_URL]

    def parse(self, response):
        resp = json.loads(response.body)
        results = []
        for status in resp['statuses']:
            items = resp2item_v2(status)
            results.extend(items)

        return results
