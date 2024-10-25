# views/email_view.py

import boto3
import logging
from config.config import AWS_REGION, SNS_TOPIC_ARN
from utils.helpers import create_email_body

class EmailView:
    def __init__(self, aws_region=AWS_REGION, topic_arn=SNS_TOPIC_ARN, logger=None):
        self.logger = logger or logging.getLogger('EmailView')
        try:
            self.sns = boto3.client('sns', region_name=aws_region)
            self.topic_arn = topic_arn
            self.logger.info("SNS 客戶端初始化成功")
        except Exception as e:
            self.logger.error(f"SNS 客戶端初始化失敗: {e}")
            self.sns = None

    def send_email(self, house_list):
        from datetime import datetime

        if not self.sns:
            self.logger.error("SNS 客戶端未初始化，無法發送郵件")
            return

        try:
            # 設定當前時間
            formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            subject = f'{formatted_time} --- 信義房屋爬蟲'

            # 創建 HTML 郵件內容
            html_message = create_email_body(house_list)

            # 發送郵件
            response = self.sns.publish(
                TopicArn=self.topic_arn,
                Message=html_message,
                Subject=subject,
                MessageStructure='html'
            )
            self.logger.info(f'郵件發送成功，Message ID: {response["MessageId"]}')
        except Exception as e:
            self.logger.error(f'發送郵件失敗: {e}')