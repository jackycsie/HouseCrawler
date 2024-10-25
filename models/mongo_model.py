# models/mongo_model.py

import pymongo
import logging
from config.config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME

class MongoModel:
    def __init__(self, uri=MONGO_URI, db_name=MONGO_DB_NAME, collection_name=MONGO_COLLECTION_NAME, logger=None):
        self.logger = logger or logging.getLogger('MongoModel')
        try:
            self.client = pymongo.MongoClient(uri)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            self.logger.info("MongoDB 連接成功")
        except pymongo.errors.PyMongoError as e:
            self.logger.error(f"MongoDB 連接失敗: {e}")
            raise e

    def find_document_by_key(self, key_name):
        try:
            document = self.collection.find_one({'key': key_name}, {'price': 1, '_id': 0})
            self.logger.debug(f"查詢鍵 {key_name} 的結果: {document}")
            return document
        except pymongo.errors.PyMongoError as e:
            self.logger.error(f"MongoDB 查詢錯誤: {e}")
            return None

    def close_connection(self):
        try:
            self.client.close()
            self.logger.info("MongoDB 連接已關閉")
        except pymongo.errors.PyMongoError as e:
            self.logger.error(f"關閉 MongoDB 連接時出錯: {e}")