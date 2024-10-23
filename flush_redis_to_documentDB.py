import redis
import pymongo
import json
import os
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

# Get credentials from environment variables
mongo_user = os.getenv('MONGO_USER')
mongo_pass = os.getenv('MONGO_PASS')

def connect(REDIS_HOST, REDIS_PORT, REDIS_SSL_CONNECTION, redis_db_instance):
    try:
        redis_connection_pool = redis.ConnectionPool(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=redis_db_instance,
            connection_class=redis.SSLConnection if REDIS_SSL_CONNECTION else redis.Connection,
            socket_timeout=10,
            socket_connect_timeout=10
        )
        redis_client = redis.Redis(connection_pool=redis_connection_pool)
        if redis_client.ping():
            print("Redis 連線成功！")
            return redis_client
        else:
            print("Redis 連線失敗")
            return False
    except Exception as err:
        print("Error while connecting Redis client >> ", str(err))
        return False

def connect_documentdb(uri):
    try:
        client = pymongo.MongoClient(uri)
        print("DocumentDB connection successful!")
        return client
    except Exception as err:
        print("Error connecting to DocumentDB: ", str(err))
        return None

redis_nodes = [
    ("crawlerdbenable-0001-001.crawlerdbenable.m0szxl.apne1.cache.amazonaws.com", 6379),
    ("crawlerdbenable-0002-001.crawlerdbenable.m0szxl.apne1.cache.amazonaws.com", 6379),
    ("crawlerdbenable-0003-001.crawlerdbenable.m0szxl.apne1.cache.amazonaws.com", 6379),
]
REDIS_PORT = 6379
REDIS_SSL_CONNECTION = True
redis_db_instance = 0
docdb_uri = f'mongodb://{mongo_user}:{mongo_pass}@sinyicrawler.cluster-c3f5m2eagzla.ap-northeast-1.docdb.amazonaws.com:27017/''?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false'
database = 'sinyi_buy_house'
collection = 'sinyi_house_info'
docdb_client = connect_documentdb(docdb_uri)
db = docdb_client[database]
col = db[collection]

# for host, port in redis_nodes:
#     redis_client = connect(host, port, REDIS_SSL_CONNECTION, redis_db_instance)
#     if redis_client:
#         cursor = '0'
#         while cursor != 0:
#             cursor, keys = redis_client.scan(cursor=cursor, count=1000)
#             for key in keys:
#                 stored_value = json.loads(redis_client.get(key).decode('utf-8'))
#                 print(key, stored_value)
#                 if stored_value:
#                     try:
#                         col.insert_one(stored_value)
#                         print(f"Data for key {key.decode()} inserted into DocumentDB.")
#                     except json.JSONDecodeError as e:
#                         print(f"Skipping key {key.decode()} due to JSON decoding error: {e}")
#                     except Exception as e:
#                         print(f"Skipping key {key.decode()} due to error: {e}")
#         redis_client.close()

# docdb_client.close()

for host, port in redis_nodes:
    redis_client = connect(host, port, REDIS_SSL_CONNECTION, redis_db_instance)
    if redis_client:
        cursor = '0'
        while cursor != 0:
            cursor, keys = redis_client.scan(cursor=cursor, count=1000)
            for key in keys:
                stored_value = json.loads(redis_client.get(key).decode('utf-8'))
                print(key, stored_value)
                if stored_value:
                    try:
                        # Add the key to the stored value dictionary
                        document = stored_value
                        document['key'] = key.decode()  # Decode and store the key

                        # Insert the document with the key into DocumentDB
                        col.insert_one(document)
                        print(f"Data for key {key.decode()} inserted into DocumentDB.")
                    except json.JSONDecodeError as e:
                        print(f"Skipping key {key.decode()} due to JSON decoding error: {e}")
                    except Exception as e:
                        print(f"Skipping key {key.decode()} due to error: {e}")
        redis_client.close()

docdb_client.close()