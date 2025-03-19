"""
日志监控模块
"""

import os
import time
import logging
from threading import Thread, Event
from typing import Dict, Any, List, Optional
from datetime import datetime

class LogMonitor:
    """日志监控类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化日志监控器

        Args:
            config (Dict[str, Any]): 监控配置
        """
        self.config = config
        self.log_path = config.get('check_log_path', './logs/training.log')
        self.markers = config.get('check_log_markers', ['Training completed', '训练完成'])
        self.check_interval = config.get('check_interval', 5)
        self.enabled = config.get('check_log_enabled', False)
        self.stop_event = Event()
        self.monitor_thread: Optional[Thread] = None
        self.start_time = datetime.now()
        self.last_position = 0
        self.logger = logging.getLogger(__name__)

    def start(self):
        """启动日志监控"""
        if not self.enabled:
            self.logger.info("日志监控未启用")
            return

        self.logger.info(f"开始监控日志文件: {self.log_path}")
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        """停止日志监控"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.stop_event.set()
            self.monitor_thread.join()
            self.logger.info("日志监控已停止")

    def _monitor_loop(self):
        """监控循环"""
        while not self.stop_event.is_set():
            try:
                if os.path.exists(self.log_path):
                    with open(self.log_path, 'r', encoding='utf-8') as f:
                        # 移动到上次读取的位置
                        f.seek(self.last_position)
                        
                        # 读取新内容
                        new_content = f.read()
                        self.last_position = f.tell()
                        
                        if new_content:
                            # 检查是否包含完成标记
                            for marker in self.markers:
                                if marker in new_content:
                                    end_time = datetime.now()
                                    duration = end_time - self.start_time
                                    self.logger.info(f"检测到完成标记: {marker}")
                                    self.logger.info(f"监控持续时间: {duration}")
                                    
                                    # 发送通知
                                    self._send_notification(marker, duration)
                                    return
                
            except Exception as e:
                self.logger.error(f"日志监控出错: {str(e)}")
            
            time.sleep(self.check_interval)

    def _send_notification(self, marker: str, duration):
        """
        发送通知

        Args:
            marker (str): 检测到的标记
            duration (timedelta): 监控持续时间
        """
        try:
            from app.core.notification import send_notification
            message = {
                "title": "训练完成通知",
                "content": f"检测到训练完成标记: {marker}",
                "duration": str(duration),
                "method": "日志监控",
                "project_name": self.config.get('project_name', '未知项目')
            }
            send_notification(message)
        except Exception as e:
            self.logger.error(f"发送通知失败: {str(e)}") 