# tests/test_html_fetcher.py

import unittest
from unittest.mock import patch, MagicMock
from utils.html_fetcher import fetch_html_content

class TestHTMLFetcher(unittest.TestCase):
    @patch('utils.html_fetcher.subprocess.run')
    def test_fetch_html_content_success(self, mock_run):
        # 設置模擬 subprocess.run 的返回值
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '<html></html>'
        
        html = fetch_html_content('http://example.com')
        self.assertEqual(html, '<html></html>')

    @patch('utils.html_fetcher.subprocess.run')
    def test_fetch_html_content_failure(self, mock_run):
        # 設置模擬 subprocess.run 的返回值
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = 'Error'
        
        html = fetch_html_content('http://example.com')
        self.assertEqual(html, '')

    @patch('utils.html_fetcher.subprocess.run', side_effect=subprocess.TimeoutExpired(cmd='curl', timeout=30))
    def test_fetch_html_content_timeout(self, mock_run):
        html = fetch_html_content('http://example.com')
        self.assertEqual(html, '')

if __name__ == '__main__':
    unittest.main()