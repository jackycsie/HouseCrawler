# tests/test_url_generator.py

import unittest
from utils.url_generator import generate_sinyi_urls

class TestURLGenerator(unittest.TestCase):
    def test_generate_sinyi_urls(self):
        price_min = 800
        price_max = 3000
        station_names = ['象山', '台北車站']
        urls = generate_sinyi_urls(price_min, price_max, station_names)
        expected_urls = [
            'https://www.sinyi.com.tw/buy/mrt/800-3000-price/Taipei-R-mrtline/02-28-mrt/publish-desc',
            'https://www.sinyi.com.tw/buy/mrt/800-3000-price/Taipei-BL-mrtline/12-mrt/publish-desc'
        ]
        self.assertEqual(urls, expected_urls)

if __name__ == '__main__':
    unittest.main()