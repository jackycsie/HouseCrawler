import redis
import json

# Redis Cluster 設定
REDIS_HOST = "clustercfg.crawlerdbenable.m0szxl.apne1.cache.amazonaws.com"
REDIS_PORT = 6379
REDIS_SSL_CONNECTION = True
redis_db_instance = 0

# 從提供的節點資訊中提取主節點 (master)
master_nodes = [
    ("crawlerdbenable-0001-001.crawlerdbenable.m0szxl.apne1.cache.amazonaws.com", 6379),
    ("crawlerdbenable-0002-001.crawlerdbenable.m0szxl.apne1.cache.amazonaws.com", 6379),
    ("crawlerdbenable-0003-001.crawlerdbenable.m0szxl.apne1.cache.amazonaws.com", 6379),
]

# 遍歷所有主節點，並打印所有鍵值對
for host, port in master_nodes:
    # 建立到單一節點的連線，使用 SSL 连接
    node_client = redis.Redis(host=host, port=port, ssl=REDIS_SSL_CONNECTION, db=redis_db_instance)

    try:
        # 使用 scan_iter 获取所有键
        print(f"正在讀取節點 {host}:{port} 的資料...")
        for key in node_client.scan_iter("*"):
            # 获取键对应的值
            value = json.loads(node_client.get(key).decode('utf-8'))
            print(key, value)
    except Exception as err:
        print(f"Error fetching data from {host}:{port} >> {err}")