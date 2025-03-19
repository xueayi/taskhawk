from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class NotificationBase(ABC):
    """基础通知类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化通知器

        Args:
            config (Dict[str, Any]): 通知配置
        """
        self.config = config
        self.enabled = config.get('enabled', False)

    @abstractmethod
    def send(self, message: Dict[str, Any]) -> bool:
        """
        发送通知

        Args:
            message (Dict[str, Any]): 通知消息

        Returns:
            bool: 发送是否成功
        """
        pass

    def _validate_config(self) -> bool:
        """
        验证配置

        Returns:
            bool: 配置是否有效
        """
        return self.enabled

    def format_message(self, message: Dict[str, Any]) -> str:
        """
        格式化消息

        Args:
            message (Dict[str, Any]): 原始消息

        Returns:
            str: 格式化后的消息
        """
        return str(message) 