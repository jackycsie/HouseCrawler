import pymongo
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取凭证
mongo_user = os.getenv('MONGO_USER')
mongo_pass = os.getenv('MONGO_PASS')

def print_specific_document(uri, database_name, collection_name, key_value):
    client = None
    try:
        # 建立 MongoDB 连接
        client = pymongo.MongoClient(uri)
        db = client[database_name]
        collection = db[collection_name]

        # 根据指定的 key 获取并打印文档
        document = collection.find_one({'key': key_value})
        if document:
            for key, value in document.items():
                print(f"{key}: {value}")
            print("-" * 30)  # 添加分隔线以区分不同的文档
        else:
            print(f"No document found with key: {key_value}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # 确保 MongoDB 客户端正确关闭
        if client:
            client.close()

# URI 和集合详情
docdb_uri = f'mongodb://{mongo_user}:{mongo_pass}@sinyicrawler.cluster-c3f5m2eagzla.ap-northeast-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false'
database = 'sinyi_buy_house'
collection = 'sinyi_house_info'
search_key = '7432VM'  # 这里设置您要搜索的 key

# 调用函数以打印特定的文档
print_specific_document(docdb_uri, database, collection, search_key)