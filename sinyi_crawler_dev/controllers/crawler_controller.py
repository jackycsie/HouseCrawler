# controllers/crawler_controller.py

import logging
from utils.url_generator import generate_sinyi_urls
from utils.html_fetcher import fetch_html_content
from utils.html_parser import extract_house_nos_from_list, extract_nearest_station, extract_house_info
from models.redis_model import RedisModel
from models.mongo_model import MongoModel
from views.email_view import EmailView
from utils.helpers import remove_duplicates, list_to_dict

class CrawlerController:
    def __init__(self, price_min, price_max, station_names, 
                 redis_model=None, mongo_model=None, email_view=None, logger=None):
        self.price_min = price_min
        self.price_max = price_max
        self.station_names = station_names
        self.logger = logger or logging.getLogger('CrawlerController')
        
        # 使用依賴注入，若未提供則實例化
        self.redis_model = redis_model or RedisModel(logger=self.logger)
        self.mongo_model = mongo_model or MongoModel(logger=self.logger)
        self.email_view = email_view or EmailView(logger=self.logger)

    def run(self):
        try:
            urls = generate_sinyi_urls(self.price_min, self.price_max, self.station_names, logger=self.logger)
            self.logger.info(f"生成的 URL 數量: {len(urls)}")
        except Exception as e:
            self.logger.error(f"生成 URL 時出錯: {e}")
            return

        house_nos = []

        for url in urls:
            try:
                self.logger.info(f"處理 URL: {url}")
                list_page_html = fetch_html_content(f"{url}/1", logger=self.logger)
                house_nos.extend(extract_house_nos_from_list(list_page_html, logger=self.logger))
                self.logger.debug(f"提取到的房屋編號數量: {len(house_nos)}")
            except Exception as e:
                self.logger.error(f"處理 URL {url} 時出錯: {e}")

        unique_house_nos = remove_duplicates(house_nos, logger=self.logger)
        self.logger.info(f"唯一的房屋編號數量: {len(unique_house_nos)}")
        send_sns_queue = []

        for house_no in unique_house_nos:
            try:
                house_url = f"https://www.sinyi.com.tw/buy/house/{house_no}"
                house_html = fetch_html_content(house_url, logger=self.logger)
                
                self.logger.info(f"處理房屋編號: {house_no}")
                nearest_stations = extract_nearest_station(house_html, self.station_names, logger=self.logger)
                if nearest_stations:
                    house_info_detail = extract_house_info(house_html, logger=self.logger)
                    nearest_station_info = [[f"nearly_station: {station}, 距離: {distance} 公尺"] for station, distance in nearest_stations]
                    house_info_detail.extend(nearest_station_info)
                    house_info_dict = list_to_dict(house_info_detail, logger=self.logger)

                    # 寫入 Redis
                    self.redis_model.set_value(house_no, house_info_dict)

                    # 檢查 MongoDB 中是否已存在
                    document = self.mongo_model.find_document_by_key(house_no)
                    if not document or document.get('price') != house_info_dict.get('price'):
                        send_sns_queue.append([house_url, house_info_detail])
                        self.logger.info(f"房屋編號 {house_no} 新增到 SNS 隊列")
            except Exception as e:
                self.logger.error(f"處理房屋編號 {house_no} 時出錯: {e}")

        # 發送 SNS 郵件
        try:
            self.email_view.send_email(send_sns_queue)
            self.logger.info("SNS 郵件發送完成")
        except Exception as e:
            self.logger.error(f"發送 SNS 郵件時出錯: {e}")

        # 關閉 MongoDB 連接
        try:
            self.mongo_model.close_connection()
        except Exception as e:
            self.logger.error(f"關閉 MongoDB 連接時出錯: {e}")