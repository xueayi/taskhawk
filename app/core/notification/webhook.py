"""
Webhook 通知模块
"""

import json
import logging
import requests
from typing import Dict, Any
from datetime import datetime
import socket

class WebhookNotification:
    """Webhook 通知类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 Webhook 通知器

        Args:
            config (Dict[str, Any]): 通知配置
        """
        if 'webhook' not in config:
            raise ValueError("配置中未找到 webhook 配置")
            
        self.config = config['webhook']
        self.logger = logging.getLogger(__name__)
        
        # 验证必要的配置项
        if not self.config.get('url'):
            raise ValueError("webhook URL 未配置")

    def send(self, message: Dict[str, Any]) -> bool:
        """
        发送 Webhook 通知

        Args:
            message (Dict[str, Any]): 通知消息

        Returns:
            bool: 是否发送成功
        """
        if not self.config.get('enabled', False):
            self.logger.info("Webhook 通知未启用")
            return False

        try:
            content = self._build_message(message)
            self.logger.debug(f"准备发送的消息内容: {json.dumps(content, ensure_ascii=False)}")
            
            response = requests.post(
                self.config['url'],
                json=content,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                self.logger.info("Webhook 通知发送成功")
                return True
            else:
                self.logger.error(f"Webhook 通知发送失败: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Webhook 通知发送出错: {str(e)}")
            return False

    def _build_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建飞书 Webhook 消息

        Args:
            message (Dict[str, Any]): 原始消息

        Returns:
            Dict[str, Any]: 飞书消息格式
        """
        content = []
        
        # 添加项目名称
        if self.config.get('include_project_name', False):
            content.append(f"**{self.config.get('include_project_name_title', '项目')}**: {message.get('project_name', '未知项目')}")

        # 添加开始时间
        if self.config.get('include_start_time', False):
            content.append(f"**{self.config.get('include_start_time_title', '开始时间')}**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 添加结束时间
        if self.config.get('include_end_time', False):
            content.append(f"**{self.config.get('include_end_time_title', '结束时间')}**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 添加检测方法
        if self.config.get('include_method', False):
            content.append(f"**{self.config.get('include_method_title', '检测方法')}**: {message.get('method', '未知方法')}")

        # 添加持续时间
        if self.config.get('include_duration', False):
            content.append(f"**{self.config.get('include_duration_title', '持续时间')}**: {message.get('duration', '未知')}")

        # 添加主机名
        if self.config.get('include_hostname', False):
            content.append(f"**{self.config.get('include_hostname_title', '主机名')}**: {socket.gethostname()}")

        # 添加消息内容
        content.append(f"**消息内容**: {message.get('content', '无内容')}")

        return {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": self.config.get('title', '通知')
                    },
                    "template": self.config.get('color', 'blue')
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": "\n".join(content)
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "content": self.config.get('footer', '此消息由 TaskNya 发送')
                            }
                        ]
                    }
                ]
            }
        } 