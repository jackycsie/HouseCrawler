# config/logger.py

import logging
import os

def setup_logger(name, log_file, level=logging.INFO):
    """創建並配置日誌記錄器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # 避免日誌向上傳播到根記錄器
    logger.propagate = False
    
    return logger

# 主日誌記錄器
MAIN_LOGGER = setup_logger('main_logger', 'logs/main.log')