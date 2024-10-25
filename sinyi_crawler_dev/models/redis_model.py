# models/redis_model.py

import redis
import json
import logging
from config.config import REDIS_HOST, REDIS_PORT, REDIS_SSL_CONNECTION, REDIS_DB_INSTANCE

class RedisModel:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, ssl=REDIS_SSL_CONNECTION, db=REDIS_DB_INSTANCE, logger=None):
        self.logger = logger or logging.getLogger('RedisModel')
        self.host = host
        self.port = port
        self.ssl = ssl
        self.db = db
        self.client = self.connect(host, port, ssl, db)
    
    def connect(self, host, port, ssl, db):
        """連接到指定的 Redis 節點"""
        try:
            client = redis.Redis(
                host=host,
                port=port,
                ssl=ssl,
                db=db,
                socket_timeout=10,
                socket_connect_timeout=10
            )
            client.ping()
            self.logger.info(f"連接到 Redis 節點 {host}:{port} 成功")
            return client
        except redis.RedisError as e:
            self.logger.error(f"連接到 Redis 節點 {host}:{port} 時出錯: {e}")
            return None
    
    def get_node_for_key(self, key):
        """取得 key 所在的 Redis 節點地址

        Args:
            key: 要查詢的 Redis 鍵。

        Returns:
            一個包含主機和端口的元組，表示 key 所在的 Redis 節點地址。
            如果發生錯誤或未找到節點，返回 None。
        """
        if not self.client:
            self.logger.error("Redis 客戶端未初始化，無法獲取節點信息")
            return None
        
        try:
            # 計算 key 所屬的槽
            slot = self.client.execute_command("CLUSTER KEYSLOT", key)
            self.logger.debug(f"鍵 {key} 所屬的槽: {slot}")
            
            # 獲取槽所在的節點信息
            cluster_nodes = self.client.execute_command("CLUSTER NODES")
            node_info = self.parse_cluster_nodes(cluster_nodes)
            
            # 查找負責該槽的 master 節點
            for node in node_info:
                if 'master' in node['flags']:
                    for slot_range in node['slots']:
                        start, end = slot_range
                        if start <= slot <= end:
                            self.logger.debug(f"鍵 {key} 位於節點 {node['host']}:{node['port']}")
                            return node['host'], node['port']
            self.logger.warning(f"未找到鍵 {key} 所在的節點")
            return None
        except redis.RedisError as e:
            self.logger.error(f"獲取鍵 {key} 所在節點時出錯: {e}")
            return None

    def parse_cluster_nodes(self, cluster_nodes_str):
        """解析 CLUSTER NODES 命令的輸出

        Args:
            cluster_nodes_str: CLUSTER NODES 的字符串輸出。

        Returns:
            一個節點信息的列表，每個節點是一個字典。
        """
        nodes = []
        lines = cluster_nodes_str.split('\n')
        for line in lines:
            if not line:
                continue
            parts = line.split()
            node = {
                'id': parts[0],
                'host': parts[1].split(':')[0],
                'port': parts[1].split(':')[1],
                'flags': parts[2].split(','),
                'slots': []
            }
            for part in parts[8:]:
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    node['slots'].append((start, end))
                elif part.isdigit():
                    slot = int(part)
                    node['slots'].append((slot, slot))
            nodes.append(node)
        self.logger.debug(f"解析後的節點信息: {nodes}")
        return nodes

    def set_value(self, key, value):
        """設置 Redis 鍵值，處理 MOVED 錯誤"""
        if not self.client:
            self.logger.error("Redis 客戶端未初始化，無法設置值")
            return
        try:
            self.client.set(key, json.dumps(value))
            self.logger.debug(f"設置 Redis 鍵 {key} 的值: {value}")
        except redis.ResponseError as e:
            if "MOVED" in str(e):
                self.handle_moved_error(e, key, value)
            else:
                self.logger.error(f"Redis 設置錯誤: {e}")

    def get_value(self, key):
        """獲取 Redis 鍵值，處理 MOVED 錯誤"""
        if not self.client:
            self.logger.error("Redis 客戶端未初始化，無法獲取值")
            return None
        try:
            value = self.client.get(key)
            if value:
                decoded_value = json.loads(value)
                self.logger.debug(f"獲取 Redis 鍵 {key} 的值: {decoded_value}")
                return decoded_value
            self.logger.debug(f"Redis 鍵 {key} 不存在")
            return None
        except redis.ResponseError as e:
            if "MOVED" in str(e):
                self.handle_moved_error(e, key)
                # 重試獲取
                try:
                    value = self.client.get(key)
                    if value:
                        decoded_value = json.loads(value)
                        self.logger.debug(f"獲取 Redis 鍵 {key} 的值: {decoded_value} 成功（重試後）")
                        return decoded_value
                    self.logger.debug(f"Redis 鍵 {key} 不存在（重試後）")
                    return None
                except Exception as e:
                    self.logger.error(f"重試獲取 Redis 鍵 {key} 時出錯: {e}")
                    return None
            else:
                self.logger.error(f"Redis 獲取錯誤: {e}")
                return None

    def handle_moved_error(self, error, key, value=None):
        """處理 MOVED 錯誤，解析目標節點並重新連接"""
        try:
            error_message = str(error)
            parts = error_message.split()
            if len(parts) >= 3:
                slot = parts[1]
                target = parts[2]
                host, port = target.split(":")
                self.logger.info(f"處理 MOVED 錯誤，鍵槽 {slot} 移動到 {host}:{port}")
                # 重新連接到目標節點
                self.client = self.connect(host, port, self.ssl, self.db)
                if self.client:
                    self.logger.info(f"成功連接到 Redis 節點 {host}:{port}")
                    if value is not None:
                        # 如果是設置操作，重試設置
                        self.set_value(key, value)
                else:
                    self.logger.error(f"無法連接到 Redis 節點 {host}:{port}")
            else:
                self.logger.error(f"無法解析 MOVED 錯誤信息: {error_message}")
        except Exception as e:
            self.logger.error(f"處理 MOVED 錯誤時出錯: {e}")