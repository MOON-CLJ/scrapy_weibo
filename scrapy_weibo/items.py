# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field


class UserItem(Item):
    id = Field()
    name = Field()
    gender = Field()
    province = Field()
    city = Field()
    location = Field()
    description = Field()
    verified = Field()
    followers_count = Field()  # 粉丝数
    statuses_count = Field()
    friends_count = Field()  # 关注数
    profile_image_url = Field()
    bi_followers_count = Field()  # 互粉数

    def to_dict(self):
        d = {}
        for k, v in self.items():
            d[k] = v
        return d


class WeiboItem(Item):
    created_at = Field()
    timestamp = Field()
    id = Field()
    mid = Field()
    text = Field()
    source = Field()
    reposts_count = Field()
    comments_count = Field()
    attitudes_count = Field()
    bmiddle_pic = Field()
    original_pic = Field()
    geo = Field()
    urls = Field()
    hashtags = Field()
    emotions = Field()
    user = Field()
    retweeted_status = Field()
    reposts = Field()

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if type(v) in [UserItem, WeiboItem]:
                d[k] = v.to_dict()
            elif type(v) == list:
                d[k] = []
                for vv in v:
                    d[k].append(vv.to_dict())
            else:
                d[k] = v
        return d
