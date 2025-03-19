from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseMonitor(ABC):
    """基础监控类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化监控器

        Args:
            config (Dict[str, Any]): 监控配置
        """
        self.config = config
        self.is_running = False

    @abstractmethod
    def start(self) -> None:
        """启动监控"""
        pass

    @abstractmethod
    def stop(self) -> None:
        """停止监控"""
        pass

    @abstractmethod
    def check_status(self) -> Dict[str, Any]:
        """
        检查状态

        Returns:
            Dict[str, Any]: 状态信息
        """
        pass

    def _validate_config(self) -> bool:
        """
        验证配置

        Returns:
            bool: 配置是否有效
        """
        return True 