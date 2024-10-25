# utils/html_parser.py

import re
from bs4 import BeautifulSoup
import logging

def extract_house_nos_from_list(html_str, logger=None):
    """從列表頁面 HTML 中提取所有房屋編號"""
    logger = logger or logging.getLogger('HTMLParser')
    try:
        pattern = r'"houseNo":"(\w{6})"'
        matches = re.findall(pattern, html_str)
        logger.debug(f"提取到的房屋編號: {matches}")
        return matches
    except Exception as e:
        logger.error(f"提取房屋編號時出錯: {e}")
        return []

def extract_nearest_station(html_str, station_names, logger=None):
    """從 HTML 中提取最近的車站資訊
    Args:
        html_str: HTML 字串。
        station_names: 車站名稱列表，每個名稱將自動加上 '站' 以符合搜索標準。

    Returns:
        一個集合，包含最近車站的名稱和距離。
    """
    logger = logger or logging.getLogger('HTMLParser')
    try:
        # 為每個車站名稱加上 "站"
        station_names = [f"{name}站" for name in station_names]

        # 創建一個字典來存儲每個車站的最近距離
        nearest_stations = {}

        # 搜索每個車站名稱並提取距離
        for station_name in station_names:
            pattern = rf'<span>{station_name}.*?<span class="life-info-map-item-time">.*?</span>'
            matches = re.findall(pattern, html_str, re.DOTALL)

            for match in matches:
                station_match = re.search(r'<span>(.*?)</span>', match)
                distance_match = re.search(r'(\d+)m', match)
                if station_match and distance_match:
                    station = station_match.group(1)
                    distance = int(distance_match.group(1))
                    if station not in nearest_stations or nearest_stations[station] > distance:
                        nearest_stations[station] = distance
                        logger.debug(f"找到最近車站: {station}, 距離: {distance} 公尺")

        # 創建一個集合來存儲最近的車站和距離
        min_distance = min(nearest_stations.values(), default=None)
        if min_distance is not None:
            nearest_stations_set = {(station, distance) for station, distance in nearest_stations.items() if distance == min_distance}
            logger.debug(f"最短距離: {min_distance} 公尺, 最近車站: {nearest_stations_set}")
        else:
            nearest_stations_set = set()
            logger.debug("未找到最近車站資訊")

        return nearest_stations_set
    except Exception as e:
        logger.error(f"提取最近車站時出錯: {e}")
        return set()

def extract_house_info(html_str, logger=None):
    """從 HTML 中提取房屋資訊（價格、建坪、格局、樓層、屋齡）"""
    logger = logger or logging.getLogger('HTMLParser')
    try:
        patterns = {
            'buy-content-title-name': r'<div class="buy-content-title-name">(.*?)</div>',
            'price': r'"priceFirst":(\d+)',
            'building_area': r'<div class="basic-title">建坪</div><div class="basic-value">([\d.]+)坪</div>',
            'layout': r'<div class="basic-title">格局</div><div class="basic-value">(.+?)</div>',
            'floor': r'<div class="basic-title">樓層</div><div class="basic-value">(.+?)</div>',
            'age': r'<div class="basic-title">屋齡</div><div class="basic-value">([\d.]+)年</div>'
        }

        filter_house_info = []

        for info_type, pattern in patterns.items():
            matches = re.findall(pattern, html_str, re.DOTALL)
            for match in matches:
                filter_house_info.append([info_type, match])
                logger.debug(f"提取 {info_type}: {match}")

        return filter_house_info
    except Exception as e:
        logger.error(f"提取房屋資訊時出錯: {e}")
        return []