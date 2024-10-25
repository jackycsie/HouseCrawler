# utils/helpers.py

import logging

def remove_duplicates(house_numbers, logger=None):
    """去除重複的房屋編號"""
    logger = logger or logging.getLogger('Helpers')
    unique_numbers = []
    for number in house_numbers:
        if number not in unique_numbers:
            unique_numbers.append(number)
    logger.debug(f"去除重複後的房屋編號數量: {len(unique_numbers)}")
    return unique_numbers

def convert_to_dict(item, logger=None):
    """將單個項目轉換為字典"""
    logger = logger or logging.getLogger('Helpers')
    if isinstance(item, list) and len(item) == 1:
        string = item[0]
        if ": " in string:
            key, value = string.split(": ", 1)
            logger.debug(f"轉換為字典: {key}: {value}")
            return {key: value}
    return {}

def list_to_dict(house_info_list, logger=None):
    """將房屋資訊列表轉換為字典"""
    logger = logger or logging.getLogger('Helpers')
    result_dict = {}
    for item in house_info_list:
        if isinstance(item, list) and len(item) == 2:
            result_dict[item[0]] = item[1]
            logger.debug(f"添加到結果字典: {item[0]}: {item[1]}")
        elif isinstance(item, list) and len(item) == 1:
            temp_dict = convert_to_dict(item, logger=logger)
            result_dict.update(temp_dict)
        else:
            logger.warning(f"意外的項目格式: {item}，將被忽略")
    return result_dict

def create_email_body(house_list, logger=None):
    """創建電子郵件的 HTML 內容"""
    logger = logger or logging.getLogger('Helpers')
    try:
        html_content = '<h1>591 租屋更新通知</h1>'
        if house_list:
            for house in house_list:
                url = house[0]
                details = {}
                if len(house) > 1:
                    # 處理除最近車站外的信息
                    for detail in house[1][:6]:  # 假設前6項是固定的房產信息
                        if len(detail) == 2:
                            key, value = detail[0], detail[1]
                            details[key] = value

                    # 將所有車站信息合併成一個字符串
                    stations = house[1][6:]
                    html_content += f'''
                    <div>
                        <h2><a href="{url}">查看詳情</a></h2>
                        <ul>
                            <li>標題: {details.get('buy-content-title-name', 'N/A')}</li>
                            <li>價格: {details.get('price', 'N/A')}</li>
                            <li>建築面積: {details.get('building_area', 'N/A')}</li>
                            <li>房型: {details.get('layout', 'N/A')}</li>
                            <li>樓層: {details.get('floor', 'N/A')}</li>
                            <li>房齡: {details.get('age', 'N/A')}</li>
                            <li>最近車站: {stations if stations else 'N/A'}</li>
                        </ul>
                    </div>
                    '''
                    logger.debug(f"添加房屋資訊到郵件內容: {url}")
        else:
            html_content += '<p>目前沒有新的資料。</p>'
            logger.debug("沒有新的房屋資料需要添加到郵件內容")
        return html_content
    except Exception as e:
        logger.error(f"創建電子郵件內容時出錯: {e}")
        return '<p>發生錯誤，無法生成郵件內容。</p>'