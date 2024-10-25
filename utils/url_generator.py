from collections import defaultdict
import logging

def generate_sinyi_urls(price_min, price_max, station_names, station_info=None, logger=None):
    logger = logger or logging.getLogger('URLGenerator')
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
        else:
            logger.warning(f"站點名稱 {name} 不在站點資訊中")

    urls = []
    for line_code, station_numbers in line_station_map.items():
        station_numbers.sort(reverse=True)
        station_numbers_str = '-'.join(station_numbers)
        url = f"https://www.sinyi.com.tw/buy/mrt/{price_min}-{price_max}-price/Taipei-{line_code}-mrtline/{station_numbers_str}-mrt/publish-desc"
        urls.append(url)
        logger.debug(f"生成的 URL: {url}")
    return urls