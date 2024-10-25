# config/config.py

import os
from dotenv import load_dotenv
from .logger import MAIN_LOGGER

# 加載環境變量
load_dotenv()

# MongoDB 設置
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASS = os.getenv('MONGO_PASS')
MONGO_URI = (
    f'mongodb://{MONGO_USER}:{MONGO_PASS}@sinyicrawler.cluster-c3f5m2eagzla.ap-northeast-1.docdb.amazonaws.com:27017/'
    f'?tls=true&tlsCAFile={os.path.join(os.path.dirname(__file__), "../certs/global-bundle.pem")}'
    '&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false'
)
MONGO_DB_NAME = 'sinyi_buy_house'
MONGO_COLLECTION_NAME = 'sinyi_house_info'

# Redis Cluster 設置
REDIS_HOST = os.getenv('REDIS_HOST', 'clustercfg.crawlerdbenable.m0szxl.apne1.cache.amazonaws.com')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_SSL_CONNECTION = os.getenv('REDIS_SSL_CONNECTION', 'True') == 'True'
REDIS_DB_INSTANCE = int(os.getenv('REDIS_DB_INSTANCE', 0))

# AWS SNS 設置
AWS_REGION = os.getenv('AWS_REGION', 'ap-northeast-1')
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN', 'arn:aws:sns:ap-northeast-1:237089372480:Rent_591')

# 日誌配置
LOG_FILE = os.getenv('LOG_FILE', 'logs/application.log')