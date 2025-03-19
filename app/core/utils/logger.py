"""
日志配置模块
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any

def setup_logger(config: Dict[str, Any]) -> None:
    """
    设置日志系统

    Args:
        config (Dict[str, Any]): 日志配置
    """
    # 创建日志目录
    log_dir = os.path.dirname(config['file'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 设置日志级别
    level = getattr(logging, config['level'].upper(), logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter(config['format'])

    # 设置文件处理器
    file_handler = RotatingFileHandler(
        filename=config['file'],
        maxBytes=config['max_size'],
        backupCount=config['backup_count'],
        encoding=config['encoding']
    )
    file_handler.setFormatter(formatter)

    # 设置控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # 设置第三方库的日志级别
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

    # 记录初始化完成
    logging.info('日志系统初始化完成') 