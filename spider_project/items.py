# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from datetime import datetime


class GoogleSearchItem(scrapy.Item):
    """谷歌搜索结果数据项"""
    title = scrapy.Field()         # 标题
    url = scrapy.Field()           # URL
    description = scrapy.Field()   # 描述
    search_query = scrapy.Field()  # 搜索关键词
    page_number = scrapy.Field()   # 页码
    crawled_at = scrapy.Field()    # 爬取时间

