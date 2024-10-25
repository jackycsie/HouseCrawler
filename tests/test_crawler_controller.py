# tests/test_crawler_controller.py

import unittest
from unittest.mock import patch, MagicMock
from controllers.crawler_controller import CrawlerController

class TestCrawlerController(unittest.TestCase):
    @patch('controllers.crawler_controller.generate_sinyi_urls')
    @patch('controllers.crawler_controller.fetch_html_content')
    @patch('controllers.crawler_controller.extract_house_nos_from_list')
    @patch('controllers.crawler_controller.remove_duplicates')
    @patch('controllers.crawler_controller.extract_nearest_station')
    @patch('controllers.crawler_controller.extract_house_info')
    def test_run(self, mock_extract_house_info, mock_extract_nearest_station, mock_remove_duplicates, 
                mock_extract_house_nos_from_list, mock_fetch_html_content, mock_generate_sinyi_urls):
        # 設置模擬返回值
        mock_generate_sinyi_urls.return_value = ['http://example.com/page1']
        mock_fetch_html_content.side_effect = ['<html></html>', '<html></html>']
        mock_extract_house_nos_from_list.return_value = ['ABC123', 'DEF456']
        mock_remove_duplicates.return_value = ['ABC123', 'DEF456']
        mock_extract_nearest_station.return_value = {('古亭', 100)}
        mock_extract_house_info.return_value = [['buy-content-title-name', 'Test House'], ['price', '1500']]

        # 創建控制器實例
        crawler = CrawlerController(800, 3000, ['古亭'])
        
        # 模擬 RedisModel 和 MongoModel
        crawler.redis_model = MagicMock()
        crawler.mongo_model = MagicMock()
        crawler.email_view = MagicMock()

        # 執行爬蟲
        crawler.run()

        # 驗證方法調用
        mock_generate_sinyi_urls.assert_called_once_with(800, 3000, ['古亭'])
        self.assertEqual(mock_fetch_html_content.call_count, 2)  # 一個列表頁面，一個房屋頁面
        self.assertEqual(mock_extract_house_nos_from_list.call_count, 1)
        mock_remove_duplicates.assert_called_once_with(['ABC123', 'DEF456'])
        mock_extract_nearest_station.assert_called_once()
        mock_extract_house_info.assert_called_once()

        # 驗證 Redis 和 MongoDB 方法
        crawler.redis_model.set_value.assert_called()
        crawler.mongo_model.find_document_by_key.assert_called()
        crawler.email_view.send_email.assert_called()

if __name__ == '__main__':
    unittest.main()