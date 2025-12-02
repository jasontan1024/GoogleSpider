# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import os


class SpiderProjectPipeline:
    """数据处理管道"""
    
    def process_item(self, item, spider):
        """
        处理每个 item
        可以在这里进行数据清洗、验证、存储等操作
        """
        adapter = ItemAdapter(item)
        
        # 清理文本数据
        if 'title' in adapter:
            adapter['title'] = adapter['title'].strip() if adapter['title'] else ''
        
        if 'description' in adapter:
            adapter['description'] = adapter['description'].strip() if adapter['description'] else ''
        
        if 'url' in adapter:
            adapter['url'] = adapter['url'].strip() if adapter['url'] else ''
        
        return item


class MongoPipeline:
    """MongoDB 存储管道"""
    
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
    
    @classmethod
    def from_crawler(cls, crawler):
        """从设置中读取 MongoDB 配置"""
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb://mongo:27017/'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'google_search'),
            mongo_collection=crawler.settings.get('MONGO_COLLECTION', 'results')
        )
    
    def open_spider(self, spider):
        """打开爬虫时连接 MongoDB"""
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.mongo_collection]
        
        # 创建唯一索引，避免重复数据
        self.collection.create_index([('url', 1), ('search_query', 1)], unique=True)
        spider.logger.info(f"已连接到 MongoDB: {self.mongo_uri}/{self.mongo_db}/{self.mongo_collection}")
    
    def close_spider(self, spider):
        """关闭爬虫时断开 MongoDB 连接"""
        self.client.close()
        spider.logger.info("已断开 MongoDB 连接")
    
    def process_item(self, item, spider):
        """处理并保存 item 到 MongoDB"""
        adapter = ItemAdapter(item)
        data = dict(adapter)
        
        try:
            # 尝试插入数据
            self.collection.insert_one(data)
            spider.logger.info(f"已保存到 MongoDB: {data.get('title', 'N/A')[:50]}")
        except DuplicateKeyError:
            # 如果数据已存在，则更新
            self.collection.update_one(
                {'url': data['url'], 'search_query': data['search_query']},
                {'$set': data}
            )
            spider.logger.debug(f"数据已存在，已更新: {data.get('url', 'N/A')}")
        except Exception as e:
            spider.logger.error(f"保存到 MongoDB 时出错: {e}")
        
        return item

