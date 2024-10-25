# tests/test_redis_model.py

import unittest
from unittest.mock import patch, MagicMock
from models.redis_model import RedisModel

class TestRedisModel(unittest.TestCase):
    @patch('models.redis_model.redis.Redis')
    def test_set_and_get_value_success(self, mock_redis):
        # 設置模擬 Redis 客戶端
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client

        redis_model = RedisModel(logger=MagicMock())

        # 測試設置值
        redis_model.set_value('key1', {'price': 1000})
        mock_client.set.assert_called_with('key1', '{"price": 1000}')

        # 測試獲取值
        mock_client.get.return_value = '{"price": 1000}'
        value = redis_model.get_value('key1')
        mock_client.get.assert_called_with('key1')
        self.assertEqual(value, {'price': 1000})

    @patch('models.redis_model.redis.Redis')
    def test_set_value_moved_error(self, mock_redis):
        # 設置模擬 Redis 客戶端，第一次設置時引發 MOVED 錯誤
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.set.side_effect = redis.ResponseError('MOVED 972 crawlerdbenable-0001-001.crawlerdbenable.m0szxl.apne1.cache.amazonaws.com:6379')
        mock_redis.return_value = mock_client

        # 創建另一個模擬 Redis 客戶端
        mock_new_client = MagicMock()
        mock_new_client.ping.return_value = True
        mock_new_client.set.return_value = True
        mock_redis.return_value = mock_new_client

        redis_model = RedisModel(logger=MagicMock())

        # 測試設置值，應處理 MOVED 錯誤並重試
        redis_model.set_value('key1', {'price': 1000})
        # 應連接到新節點並設置值
        mock_new_client.set.assert_called_with('key1', '{"price": 1000}')

    @patch('models.redis_model.redis.Redis')
    def test_get_value_moved_error(self, mock_redis):
        # 設置模擬 Redis 客戶端，第一次獲取時引發 MOVED 錯誤
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.get.side_effect = redis.ResponseError('MOVED 972 crawlerdbenable-0001-001.crawlerdbenable.m0szxl.apne1.cache.amazonaws.com:6379')
        mock_redis.return_value = mock_client

        # 創建另一個模擬 Redis 客戶端
        mock_new_client = MagicMock()
        mock_new_client.ping.return_value = True
        mock_new_client.get.return_value = '{"price": 1000}'
        mock_redis.return_value = mock_new_client

        redis_model = RedisModel(logger=MagicMock())

        # 測試獲取值，應處理 MOVED 錯誤並重試
        value = redis_model.get_value('key1')
        mock_new_client.get.assert_called_with('key1')
        self.assertEqual(value, {'price': 1000})

    @patch('models.redis_model.redis.Redis')
    def test_handle_moved_error_invalid_format(self, mock_redis):
        # 設置模擬 Redis 客戶端，引發無法解析的 MOVED 錯誤
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.set.side_effect = redis.ResponseError('MOVED_INVALID_FORMAT')
        mock_redis.return_value = mock_client

        redis_model = RedisModel(logger=MagicMock())

        # 測試設置值，應記錄錯誤並不嘗試重試
        redis_model.set_value('key1', {'price': 1000})
        # 不應有其他設置調用
        mock_client.set.assert_called_once_with('key1', '{"price": 1000}')

    @patch('models.redis_model.redis.Redis')
    def test_connection_error(self, mock_redis):
        # 設置模擬 Redis 連接失敗
        mock_redis.side_effect = redis.RedisError("連接失敗")
        
        with self.assertRaises(redis.RedisError):
            RedisModel(logger=MagicMock())

if __name__ == '__main__':
    unittest.main()