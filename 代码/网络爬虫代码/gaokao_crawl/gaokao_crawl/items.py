# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class GaokaoCrawlItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    raw_key = Field() # 被爬取网站的主键
    domain = Field() # 被爬网站的标识
    url = Field() # 爬取url
    category = Field()  # 页面类别,列表页or详情页
    html = Field()
    scraped_time = Field()

    college = Field() # 录取学校
    major = Field() # 录取专业
    area = Field() # 地区
    year = Field() # 年份 例如 2016
    branch = Field() # 文理科别
    batch = Field() # 批次
    ave_score = Field() # 平均分
    low_score = Field() # 最低分
    hig_score = Field() # 最高分
    number = Field() # 报考考生数量


    def __repr__(self):
        """only print out summary after exiting the Pipeline"""
        return repr({
            "summary": "{} on {}".format(self['url'], self['category'])
        })
