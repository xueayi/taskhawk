"""
邮件通知模块
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from datetime import datetime

class EmailNotification:
    """邮件通知类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化邮件通知器

        Args:
            config (Dict[str, Any]): 通知配置
        """
        if 'email' not in config:
            raise ValueError("配置中未找到邮件配置")
            
        self.config = config['email']
        self.logger = logging.getLogger(__name__)
        
        # 验证必要的配置项
        required_fields = ['smtp_server', 'smtp_port', 'username', 'password', 'from_address', 'to_addresses']
        for field in required_fields:
            if not self.config.get(field):
                raise ValueError(f"邮件配置缺少必要字段: {field}")

    def send(self, message: Dict[str, Any]) -> bool:
        """
        发送邮件通知

        Args:
            message (Dict[str, Any]): 通知消息

        Returns:
            bool: 是否发送成功
        """
        if not self.config.get('enabled', False):
            self.logger.info("邮件通知未启用")
            return False

        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.get('title', '训练完成通知')
            msg['From'] = self.config['from_address']
            msg['To'] = ', '.join(self.config['to_addresses'])

            # 构建邮件内容
            html_content = self._build_html_content(message)
            msg.attach(MIMEText(html_content, 'html'))

            # 连接SMTP服务器并发送
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                if self.config.get('use_tls', True):
                    server.starttls()
                server.login(self.config['username'], self.config['password'])
                server.send_message(msg)

            self.logger.info("邮件通知发送成功")
            return True

        except Exception as e:
            self.logger.error(f"邮件通知发送失败: {str(e)}")
            return False

    def _build_html_content(self, message: Dict[str, Any]) -> str:
        """
        构建HTML格式的邮件内容

        Args:
            message (Dict[str, Any]): 通知消息

        Returns:
            str: HTML格式的邮件内容
        """
        # 基本样式
        style = """
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: #4CAF50; color: white; padding: 10px; text-align: center; }
            .content { background-color: #f9f9f9; padding: 20px; }
            .footer { text-align: center; padding: 10px; color: #666; }
            .info-item { margin: 10px 0; }
            .label { font-weight: bold; }
        </style>
        """

        # 构建内容
        content_items = []
        
        # 添加项目名称
        if 'project_name' in message:
            content_items.append(f'<div class="info-item"><span class="label">项目：</span>{message["project_name"]}</div>')

        # 添加检测方法
        if 'method' in message:
            content_items.append(f'<div class="info-item"><span class="label">检测方法：</span>{message["method"]}</div>')

        # 添加持续时间
        if 'duration' in message:
            content_items.append(f'<div class="info-item"><span class="label">持续时间：</span>{message["duration"]}</div>')

        # 添加主要内容
        if 'content' in message:
            content_items.append(f'<div class="info-item"><span class="label">详细信息：</span>{message["content"]}</div>')

        # 组装HTML
        html = f"""
        <html>
        <head>{style}</head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{message.get('title', '训练完成通知')}</h2>
                </div>
                <div class="content">
                    {''.join(content_items)}
                </div>
                <div class="footer">
                    <p>此消息由 TaskNya 自动发送</p>
                    <p>发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html 