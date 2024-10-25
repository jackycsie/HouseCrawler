import subprocess
import logging

def fetch_html_content(url, logger=None):
    """使用 curl 獲取指定網址的 HTML 內容"""
    logger = logger or logging.getLogger('HTMLFetcher')
    try:
        curl_command = f"curl -k {url}"
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            logger.error(f"curl 命令失敗，URL: {url}, 錯誤: {result.stderr}")
            return ""
        logger.debug(f"成功抓取 URL: {url}")
        return result.stdout
    except subprocess.TimeoutExpired:
        logger.error(f"curl 命令超時，URL: {url}")
        return ""
    except Exception as e:
        logger.error(f"抓取 URL {url} 時出錯: {e}")
        return ""