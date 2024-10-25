# main.py

import os
import logging
from config.logger import setup_logger
from controllers.crawler_controller import CrawlerController

def main():
    # 確保日誌目錄存在
    os.makedirs('logs', exist_ok=True)
    
    # 設置主日誌記錄器
    logger = setup_logger('main_logger', 'logs/main.log')
    logger.info("應用程序啟動")

    try:
        price_min = 800
        price_max = 3000
        station_names = ['南京復興, 大坪林']  # 您可以根據需要修改站點名稱

        crawler = CrawlerController(price_min, price_max, station_names, logger=logger)
        crawler.run()
    except Exception as e:
        logger.critical(f"應用程序發生致命錯誤: {e}")
    finally:
        logger.info("應用程序結束")

if __name__ == "__main__":
    main()
