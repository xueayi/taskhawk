"""
文件监控模块
"""

import os
import time
import logging
from threading import Thread, Event
from typing import Dict, Any, Optional
from datetime import datetime

class FileMonitor:
    """文件监控类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化文件监控器

        Args:
            config (Dict[str, Any]): 监控配置
        """
        self.config = config
        self.file_path = config['check_file_path']
        self.check_interval = config['check_interval']
        self.stop_event = Event()
        self.monitor_thread: Optional[Thread] = None
        self.start_time = datetime.now()
        self.logger = logging.getLogger(__name__)

    def start(self):
        """启动文件监控"""
        if not self.config['check_file_enabled']:
            self.logger.info("文件监控未启用")
            return

        self.logger.info(f"开始监控文件: {self.file_path}")
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        """停止文件监控"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.stop_event.set()
            self.monitor_thread.join()
            self.logger.info("文件监控已停止")

    def _monitor_loop(self):
        """监控循环"""
        while not self.stop_event.is_set():
            try:
                if os.path.exists(self.file_path):
                    end_time = datetime.now()
                    duration = end_time - self.start_time
                    self.logger.info(f"检测到目标文件: {self.file_path}")
                    self.logger.info(f"监控持续时间: {duration}")
                    
                    # 发送通知
                    self._send_notification(duration)
                    break
                
            except Exception as e:
                self.logger.error(f"文件监控出错: {str(e)}")
            
            time.sleep(self.check_interval)

    def _send_notification(self, duration):
        """
        发送通知

        Args:
            duration (timedelta): 监控持续时间
        """
        try:
            from app.core.notification import send_notification
            message = {
                "title": "文件生成通知",
                "content": f"文件 {self.file_path} 已生成",
                "duration": str(duration),
                "method": "文件监控"
            }
            send_notification(message)
        except Exception as e:
            self.logger.error(f"发送通知失败: {str(e)}") 