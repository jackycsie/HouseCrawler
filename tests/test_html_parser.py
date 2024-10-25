# tests/test_html_parser.py

import unittest
from utils.html_parser import extract_house_nos_from_list, extract_nearest_station, extract_house_info

class TestHTMLParser(unittest.TestCase):
    def test_extract_house_nos_from_list(self):
        html = '<div>"houseNo":"ABC123"</div><div>"houseNo":"DEF456"</div>'
        house_nos = extract_house_nos_from_list(html)
        self.assertEqual(house_nos, ['ABC123', 'DEF456'])

    def test_extract_nearest_station(self):
        html = '''
        <span>古亭站</span><span class="life-info-map-item-time">100m</span>
        <span>中山站</span><span class="life-info-map-item-time">200m</span>
        '''
        station_names = ['古亭', '中山']
        nearest = extract_nearest_station(html, station_names)
        self.assertEqual(nearest, {('古亭', 100)})

    def test_extract_house_info(self):
        html = '''
        <div class="buy-content-title-name">漂亮的房子</div>
        "priceFirst":1500
        <div class="basic-title">建坪</div><div class="basic-value">30坪</div>
        <div class="basic-title">格局</div><div class="basic-value">3房2廳</div>
        <div class="basic-title">樓層</div><div class="basic-value">5/10</div>
        <div class="basic-title">屋齡</div><div class="basic-value">5年</div>
        '''
        house_info = extract_house_info(html)
        expected = [
            ['buy-content-title-name', '漂亮的房子'],
            ['price', '1500'],
            ['building_area', '30'],
            ['layout', '3房2廳'],
            ['floor', '5/10'],
            ['age', '5']
        ]
        self.assertEqual(house_info, expected)

if __name__ == '__main__':
    unittest.main()