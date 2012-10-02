# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field


class UserItem(Item):
    uid = Field()
    name = Field()
    gender = Field()
    location = Field()
    description = Field()
    verified = Field()
    followers_count = Field()
    statuses_count = Field()
    friends_count = Field()


class WeiboItem(Item):
    created_at = Field()
    id = Field()
    mid = Field()
    text = Field()
    source = Field()
    comments_count = Field()
    geo = Field()
    urls = Field()
    hashtags = Field()
    emotions = Field()
    user = Field()
    retweeted_status = Field()
