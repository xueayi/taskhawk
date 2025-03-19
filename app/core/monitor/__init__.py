"""
TaskNya 监控模块
"""

import logging
from typing import Dict, Any
from .file_monitor import FileMonitor
from .log_monitor import LogMonitor
from .gpu_monitor import GPUMonitor

# 全局监控器实例
_monitors = []

def start_monitors(config: Dict[str, Any]) -> None:
    """
    启动所有监控服务

    Args:
        config (Dict[str, Any]): 监控配置
    """
    logger = logging.getLogger(__name__)
    logger.info("正在启动监控服务...")

    # 启动文件监控
    try:
        file_monitor = FileMonitor(config)
        file_monitor.start()
        _monitors.append(file_monitor)
        logger.info("文件监控服务已启动")
    except Exception as e:
        logger.error(f"启动文件监控服务失败: {str(e)}")

    # 启动日志监控
    try:
        log_monitor = LogMonitor(config)
        log_monitor.start()
        _monitors.append(log_monitor)
        logger.info("日志监控服务已启动")
    except Exception as e:
        logger.error(f"启动日志监控服务失败: {str(e)}")

    # 启动 GPU 监控
    try:
        gpu_monitor = GPUMonitor(config)
        gpu_monitor.start()
        _monitors.append(gpu_monitor)
        logger.info("GPU 监控服务已启动")
    except Exception as e:
        logger.error(f"启动 GPU 监控服务失败: {str(e)}")

def stop_monitors() -> None:
    """停止所有监控服务"""
    logger = logging.getLogger(__name__)
    logger.info("正在停止所有监控服务...")
    
    for monitor in _monitors:
        try:
            monitor.stop()
        except Exception as e:
            logger.error(f"停止监控服务失败: {str(e)}")
    
    _monitors.clear()
    logger.info("所有监控服务已停止") 