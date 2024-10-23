import subprocess
import re
import redis
import json
import pymongo
from bs4 import BeautifulSoup
from collections import defaultdict

def generate_sinyi_urls(price_min, price_max, station_names):
    # 站點資料，包含站名、路線代號和站號
    station_info = {
        # 淡水信義線 (Red Line, R)
        '象山': {'line_code': 'R', 'station_number': '02'},
        '台北101/世貿': {'line_code': 'R', 'station_number': '03'},
        '信義安和': {'line_code': 'R', 'station_number': '04'},
        '大安': {'line_code': 'R', 'station_number': '05'},
        '大安森林公園': {'line_code': 'R', 'station_number': '06'},
        '東門': {'line_code': 'R', 'station_number': '07'},
        '中正紀念堂': {'line_code': 'R', 'station_number': '08'},
        '台大醫院': {'line_code': 'R', 'station_number': '09'},
        '台北車站': {'line_code': 'R', 'station_number': '10'},
        '中山': {'line_code': 'R', 'station_number': '11'},
        '雙連': {'line_code': 'R', 'station_number': '12'},
        '民權西路': {'line_code': 'R', 'station_number': '13'},
        '圓山': {'line_code': 'R', 'station_number': '14'},
        '劍潭': {'line_code': 'R', 'station_number': '15'},
        '士林': {'line_code': 'R', 'station_number': '16'},
        '芝山': {'line_code': 'R', 'station_number': '17'},
        '明德': {'line_code': 'R', 'station_number': '18'},
        '石牌': {'line_code': 'R', 'station_number': '19'},
        '唭哩岸': {'line_code': 'R', 'station_number': '20'},
        '奇岩': {'line_code': 'R', 'station_number': '21'},
        '北投': {'line_code': 'R', 'station_number': '22'},
        '新北投': {'line_code': 'R', 'station_number': '22A'},  # 支線
        '復興崗': {'line_code': 'R', 'station_number': '23'},
        '忠義': {'line_code': 'R', 'station_number': '24'},
        '關渡': {'line_code': 'R', 'station_number': '25'},
        '竹圍': {'line_code': 'R', 'station_number': '26'},
        '紅樹林': {'line_code': 'R', 'station_number': '27'},
        '淡水': {'line_code': 'R', 'station_number': '28'},
        
        # 板南線 (Blue Line, BL)
        '頂埔': {'line_code': 'BL', 'station_number': '01'},
        '永寧': {'line_code': 'BL', 'station_number': '02'},
        '土城': {'line_code': 'BL', 'station_number': '03'},
        '海山': {'line_code': 'BL', 'station_number': '04'},
        '亞東醫院': {'line_code': 'BL', 'station_number': '05'},
        '府中': {'line_code': 'BL', 'station_number': '06'},
        '板橋': {'line_code': 'BL', 'station_number': '07'},
        '新埔': {'line_code': 'BL', 'station_number': '08'},
        '江子翠': {'line_code': 'BL', 'station_number': '09'},
        '龍山寺': {'line_code': 'BL', 'station_number': '10'},
        '西門': {'line_code': 'BL', 'station_number': '11'},
        '台北車站': {'line_code': 'BL', 'station_number': '12'},
        '善導寺': {'line_code': 'BL', 'station_number': '13'},
        '忠孝新生': {'line_code': 'BL', 'station_number': '14'},
        '忠孝復興': {'line_code': 'BL', 'station_number': '15'},
        '忠孝敦化': {'line_code': 'BL', 'station_number': '16'},
        '國父紀念館': {'line_code': 'BL', 'station_number': '17'},
        '市政府': {'line_code': 'BL', 'station_number': '18'},
        '永春': {'line_code': 'BL', 'station_number': '19'},
        '後山埤': {'line_code': 'BL', 'station_number': '20'},
        '昆陽': {'line_code': 'BL', 'station_number': '21'},
        '南港': {'line_code': 'BL', 'station_number': '22'},
        '南港展覽館': {'line_code': 'BL', 'station_number': '23'},

        # 松山新店線 (Green Line, G)
        '新店': {'line_code': 'G', 'station_number': '01'},
        '新店區公所': {'line_code': 'G', 'station_number': '02'},
        '七張': {'line_code': 'G', 'station_number': '03'},
        '小碧潭': {'line_code': 'G', 'station_number': '03A'},  # 支線
        '大坪林': {'line_code': 'G', 'station_number': '04'},
        '景美': {'line_code': 'G', 'station_number': '05'},
        '萬隆': {'line_code': 'G', 'station_number': '06'},
        '公館': {'line_code': 'G', 'station_number': '07'},
        '台電大樓': {'line_code': 'G', 'station_number': '08'},
        '古亭': {'line_code': 'G', 'station_number': '09'},
        '中正紀念堂': {'line_code': 'G', 'station_number': '10'},
        '小南門': {'line_code': 'G', 'station_number': '11'},
        '西門': {'line_code': 'G', 'station_number': '12'},
        '北門': {'line_code': 'G', 'station_number': '13'},
        '中山': {'line_code': 'G', 'station_number': '14'},
        '松江南京': {'line_code': 'G', 'station_number': '15'},
        '南京復興': {'line_code': 'G', 'station_number': '16'},
        '台北小巨蛋': {'line_code': 'G', 'station_number': '17'},
        '南京三民': {'line_code': 'G', 'station_number': '18'},
        '松山': {'line_code': 'G', 'station_number': '19'},

        # 中和新蘆線 (Orange Line, O)
        '南勢角': {'line_code': 'O', 'station_number': '01'},
        '景安': {'line_code': 'O', 'station_number': '02'},
        '永安市場': {'line_code': 'O', 'station_number': '03'},
        '頂溪': {'line_code': 'O', 'station_number': '04'},
        '古亭': {'line_code': 'O', 'station_number': '05'},
        '東門': {'line_code': 'O', 'station_number': '06'},
        '忠孝新生': {'line_code': 'O', 'station_number': '07'},
        '松江南京': {'line_code': 'O', 'station_number': '08'},
        '行天宮': {'line_code': 'O', 'station_number': '09'},
        '中山國小': {'line_code': 'O', 'station_number': '10'},
        '民權西路': {'line_code': 'O', 'station_number': '11'},
        '大橋頭': {'line_code': 'O', 'station_number': '12'},
        '台北橋': {'line_code': 'O', 'station_number': '13'},
        '菜寮': {'line_code': 'O', 'station_number': '14'},
        '三重': {'line_code': 'O', 'station_number': '15'},
        '先嗇宮': {'line_code': 'O', 'station_number': '16'},
        '頭前庄': {'line_code': 'O', 'station_number': '17'},
        '新莊': {'line_code': 'O', 'station_number': '18'},
        '輔大': {'line_code': 'O', 'station_number': '19'},
        '丹鳳': {'line_code': 'O', 'station_number': '20'},
        '迴龍': {'line_code': 'O', 'station_number': '21'},

        # 文湖線 (Brown Line, BR)
        '動物園': {'line_code': 'BR', 'station_number': '01'},
        '木柵': {'line_code': 'BR', 'station_number': '02'},
        '萬芳社區': {'line_code': 'BR', 'station_number': '03'},
        '萬芳醫院': {'line_code': 'BR', 'station_number': '04'},
        '辛亥': {'line_code': 'BR', 'station_number': '05'},
        '麟光': {'line_code': 'BR', 'station_number': '06'},
        '六張犁': {'line_code': 'BR', 'station_number': '07'},
        '科技大樓': {'line_code': 'BR', 'station_number': '08'},
        '大安': {'line_code': 'BR', 'station_number': '09'},
        '忠孝復興': {'line_code': 'BR', 'station_number': '10'},
        '南京復興': {'line_code': 'BR', 'station_number': '11'},
        '中山國中': {'line_code': 'BR', 'station_number': '12'},
        '松山機場': {'line_code': 'BR', 'station_number': '13'},
        '大直': {'line_code': 'BR', 'station_number': '14'},
        '劍南路': {'line_code': 'BR', 'station_number': '15'},
        '西湖': {'line_code': 'BR', 'station_number': '16'},
        '港墘': {'line_code': 'BR', 'station_number': '17'},
        '文德': {'line_code': 'BR', 'station_number': '18'},
        '內湖': {'line_code': 'BR', 'station_number': '19'},
        '大湖公園': {'line_code': 'BR', 'station_number': '20'},
        '葫洲': {'line_code': 'BR', 'station_number': '21'},
        '東湖': {'line_code': 'BR', 'station_number': '22'},
        '南港軟體園區': {'line_code': 'BR', 'station_number': '23'},
        '南港展覽館': {'line_code': 'BR', 'station_number': '24'},

        # 環狀線 (Yellow Line, Y)
        '大坪林': {'line_code': 'Y', 'station_number': '09'},
        '十四張': {'line_code': 'Y', 'station_number': '08'},
        '秀朗橋': {'line_code': 'Y', 'station_number': '07'},
        '景平': {'line_code': 'Y', 'station_number': '06'},
        '景安': {'line_code': 'Y', 'station_number': '05'},
        '中和': {'line_code': 'Y', 'station_number': '04'},
        '橋和': {'line_code': 'Y', 'station_number': '03'},
        '中原': {'line_code': 'Y', 'station_number': '02'},
        '板新': {'line_code': 'Y', 'station_number': '01'}
    }
    line_station_map = defaultdict(list)
    for name in station_names:
        if name in station_info:
            info = station_info[name]
            line_station_map[info['line_code']].append(info['station_number'])

    urls = []
    for line_code, station_numbers in line_station_map.items():
        station_numbers.sort(reverse=True)
        station_numbers_str = '-'.join(station_numbers)
        url = f"https://www.sinyi.com.tw/buy/mrt/{price_min}-{price_max}-price/Taipei-{line_code}-mrtline/{station_numbers_str}-mrt/publish-desc"
        urls.append(url)
    return urls

def fetch_html_content(url):
    """使用 curl 獲取指定網址的 HTML 內容"""
    curl_command = f"curl -k {url}"
    result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
    return result.stdout

def extract_house_nos_from_list(html_str):
    """從列表頁面 HTML 中提取所有房屋編號"""
    pattern = r'"houseNo":"(\w{6})"'
    matches = re.findall(pattern, html_str)
    return matches

# def extract_nearest_station(html_str, station_name='信義安和站'):
#     """從 HTML 中提取最近的車站資訊"""
#     pattern = rf'<span>{station_name}.*?<span class="life-info-map-item-time">.*?</span>'
#     matches = re.findall(pattern, html_str)

#     stations = []
#     for match in matches:
#         station_match = re.search(r'<span>(.*?)</span>', match)
#         distance_match = re.search(r'(\d+)m', match)
#         if station_match and distance_match:
#             stations.append({'station': station_match.group(1), 'distance': int(distance_match.group(1))})

#     nearest_stations_set = set((station['station'], station['distance'])
#                                 for station in stations if station['distance'] == min(s['distance'] for s in stations))

#     # for station_name, distance in nearest_stations_set:
#     #     print(f"最近的車站: {station_name}, 距離: {distance} 公尺")

#     return nearest_stations_set

def extract_nearest_station(html_str, station_names):
    """從 HTML 中提取最近的車站資訊
    Args:
        html_str: HTML 字串。
        station_names: 車站名稱列表，每個名稱將自動加上 '站' 以符合搜索標準。

    Returns:
        一個集合，包含最近車站的名稱和距離。
    """
    # 為每個車站名稱加上 "站"
    station_names = [f"{name}站" for name in station_names]

    # 創建一個字典來存儲每個車站的最近距離
    nearest_stations = {}

    # 搜索每個車站名稱並提取距離
    for station_name in station_names:
        pattern = rf'<span>{station_name}.*?<span class="life-info-map-item-time">.*?</span>'
        matches = re.findall(pattern, html_str)

        for match in matches:
            station_match = re.search(r'<span>(.*?)</span>', match)
            distance_match = re.search(r'(\d+)m', match)
            if station_match and distance_match:
                station = station_match.group(1)
                distance = int(distance_match.group(1))
                if station not in nearest_stations or nearest_stations[station] > distance:
                    nearest_stations[station] = distance

    # 創建一個集合來存儲最近的車站和距離
    min_distance = min(nearest_stations.values(), default=None)
    nearest_stations_set = {(station, distance) for station, distance in nearest_stations.items() if distance == min_distance}

    return nearest_stations_set

def extract_house_info(html_str):
    """從 HTML 中提取房屋資訊（價格、建坪、格局、樓層、屋齡）"""
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
        matches = re.findall(pattern, html_str)
        for match in matches:
            filter_house_info.append([info_type, match])
            # print(filter_house_info)

    return filter_house_info

def connect(REDIS_HOST, REDIS_PORT, REDIS_SSL_CONNECTION, redis_db_instance):
    try:
        # Check if SSL connection is required
        is_ssl_connection = REDIS_SSL_CONNECTION

        # Create a Redis connection pool with SSL/TLS support
        redis_connection_pool = redis.ConnectionPool(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=redis_db_instance,
            connection_class=redis.SSLConnection if is_ssl_connection else redis.Connection,
            socket_timeout=10,  # 设置超时为10秒
            socket_connect_timeout=10
        )

        # Create a Redis client using the connection pool
        redis_client = redis.Redis(connection_pool=redis_connection_pool)

        # Check if the Redis connection is successful by sending a PING
        if redis_client.ping():
            print("Redis 連線成功！")

            # Fetch and print Redis server info
            # redis_info = redis_client.info()
            # print("Redis 伺服器資訊：")
            # print(json.dumps(redis_info, indent=4))

            return redis_client
        else:
            print("Redis 連線失敗")
            return False
    except Exception as err:
        print("Error while connecting Redis client >> ", str(err))
        return False

def get_node_for_key(redis_client, key):  
    """取得 key 所在的 Redis 節點地址。

    Args:
        redis_client: 連接到 Redis 集群中任意一個節點的客戶端對象。
        key: 要查詢的 Redis 鍵。

    Returns:
        一個包含主機和端口的元組，表示 key 所在的 Redis 節點地址。
        如果發生錯誤或未找到節點，返回 None。
    """

    try:
        # 計算 key 所屬的槽
        slot = redis_client.execute_command("CLUSTER KEYSLOT", key)

        # 獲取槽所在的節點信息
        node_info = redis_client.execute_command("CLUSTER NODES")

        # 解析節點信息（現在 node_info 是一個字典）
        for node_addr, node_data in node_info.items():
            if 'master' in node_data['flags']:  # 只考慮 master 節點
                slot_range = node_data['slots']
                # 檢查 slot 是否在節點負責的槽範圍內, 並將 slot_start 和 slot_end 轉換為整數
                if any(int(slot_start) <= slot <= int(slot_end) for slot_start, slot_end in slot_range):
                    # 直接從 node_addr 中提取主機和端口
                    host, port = node_addr.split(":")
                    return host, port[:4]

        # 如果未找到節點，返回 None
        return None

    except redis.exceptions.ResponseError as e:
        # 處理其他 Redis 錯誤，例如集群不可用
        print(f"Redis 錯誤: {str(e)}")
        return None, None

def get_value_or_none(key):
    """
    從 DocumentDB 獲取指定鍵的值，如果鍵不存在或值為空，則返回 None。

    Args:
        key: 要查詢的鍵。

    Returns:
        鍵的值，如果鍵不存在或值為空，則返回 None。
    """

    client = pymongo.MongoClient('mongodb://jacky:testlab1@docdb-2024-09-18-06-26-02.cluster-c3f5m2eagzla.ap-northeast-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false')

    db = client['your_database_name']
    collection = db['your_collection_name']

    # 執行查詢
    result = collection.find_one({key: {"$exists": True}}) 

    # 檢查結果並處理
    if result and result[key]:  # 確保鍵存在且值不為空
        return result[key]
    else:
        return None

def write_db(redis_client, key, value):
    try:
        check_docDB_data = None
        host, port = get_node_for_key(redis_client, key)
        if host and port:
            node_client = connect(host, port, REDIS_SSL_CONNECTION, redis_db_instance)
            # 使用 JSON 格式序列化 value
            node_client.set(key, json.dumps(value))
            # 获取键值，并使用 JSON 解析回原始格式
            stored_value = json.loads(node_client.get(key).decode('utf-8'))
            # print(stored_value)
        else:
            # 同样使用 JSON 格式序列化并存储
            redis_client.set(key, json.dumps(value))
            # 解析存储的值
            check_docDB_data = json.loads(redis_client.get(key).decode('utf-8'))
        return check_docDB_data
    except Exception as e:
        print(f"Error writing to Redis: {e}")
        return None

# Function to remove duplicates and return a list with only unique house numbers
def remove_duplicates(house_numbers):
    unique_numbers = []  # List to store only unique numbers

    for number in house_numbers:
        if number not in unique_numbers:
            unique_numbers.append(number)  # Add the number if it's not already in the list

    return unique_numbers

def convert_to_dict(item):
    # 从列表中提取字符串
    string = item[0] if isinstance(item, list) else item
    # 分割键和值
    key, value = string.split(": ", 1)
    # 创建并返回字典
    return {key: value}

def list_to_dict(house_info_list):
    result_dict = {}
    for item in house_info_list:
        if isinstance(item, list) and len(item) == 2:
            # 正常的键值对列表
            result_dict[item[0]] = item[1]
        elif isinstance(item, list) and len(item) == 1:
            # 非标准单项列表，可能是近站信息的情况
            temp_dict = convert_to_dict(item)
            result_dict.update(temp_dict)
        else:
            print(f"Error: Unexpected item format in {item}. This item will be ignored.")
    return result_dict


if __name__ == "__main__":
    price_min = 800
    price_max = 3000
    station_names = ['大安', '信義安和', '南京復興'] 
    urls = generate_sinyi_urls(price_min, price_max, station_names)

    REDIS_HOST = "clustercfg.crawlerdbenable.m0szxl.apne1.cache.amazonaws.com"
    REDIS_PORT = 6379
    REDIS_SSL_CONNECTION = True
    redis_db_instance = 0
    redis_client = connect(REDIS_HOST, REDIS_PORT, REDIS_SSL_CONNECTION, redis_db_instance)

    house_nos = []

    for url in urls:
        i = 1
        while i < 4:
            print("page ", i)
            list_page_html = fetch_html_content(url+"/"+str(i))
            house_nos.extend(extract_house_nos_from_list(list_page_html))
            i = i+1 
    unique_house_nos = remove_duplicates(house_nos)

    for house_no in unique_house_nos:
        house_url = f"https://www.sinyi.com.tw/buy/house/{house_no}"
        house_html = fetch_html_content(house_url)

        soup = BeautifulSoup(house_html, 'html.parser')
        house_str = str(soup)

        print(f"\n=== 房屋編號: {house_no} ===") 
        nearest_stations = extract_nearest_station(house_str, station_names)
        # print(check_distance_noise)
        if nearest_stations != set():
            house_info_detail = extract_house_info(house_str)
            nearest_station_info = [[f"nearly_station: {station_name}, 距離: {distance} 公尺"] for station_name, distance in nearest_stations]
            house_info_detail.extend(nearest_station_info)
            # print(house_info_detail)
            house_info_dict = list_to_dict(house_info_detail)
            # print(house_info_dict)
            check_docDB_data = write_db(redis_client, house_no, house_info_dict)

        