# tests/test_mongo_model.py

import unittest
from unittest.mock import patch, MagicMock
from models.mongo_model import MongoModel

class TestMongoModel(unittest.TestCase):
    @patch('models.mongo_model.pymongo.MongoClient')
    def test_find_document_by_key(self, mock_mongo_client):
        # 設置模擬數據庫和集合
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {'price': 1000}
        
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        
        mock_client = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        mock_mongo_client.return_value = mock_client
        
        # 初始化 MongoModel
        mongo_model = MongoModel()
        
        # 執行查詢
        result = mongo_model.find_document_by_key('house123')
        
        # 驗證結果
        self.assertEqual(result, {'price': 1000})
        mock_collection.find_one.assert_called_with({'key': 'house123'}, {'price': 1, '_id': 0})

    @patch('models.mongo_model.pymongo.MongoClient')
    def test_close_connection(self, mock_mongo_client):
        # 初始化 MongoModel
        mongo_model = MongoModel()
        mongo_model.close_connection()
        
        # 驗證關閉連接被調用
        mock_mongo_client.return_value.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()