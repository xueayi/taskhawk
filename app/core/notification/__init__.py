"""
TaskNya 通知模块
"""

import logging
from typing import Dict, Any, List
from .webhook import WebhookNotification
from .email_notification import EmailNotification

# 全局通知器实例列表
_notifiers = []

def init_notification(config: Dict[str, Any]) -> None:
    """
    初始化通知系统

    Args:
        config (Dict[str, Any]): 通知配置
    """
    logger = logging.getLogger(__name__)

    if 'notification' not in config:
        logger.warning("配置中未找到通知配置，跳过通知系统初始化")
        return

    notification_config = config['notification']

    # 初始化 Webhook 通知
    try:
        webhook = WebhookNotification(notification_config)
        _notifiers.append(webhook)
    except Exception as e:
        logger.error(f"Webhook 通知初始化失败: {str(e)}")

    # 初始化邮件通知
    try:
        email = EmailNotification(notification_config)
        _notifiers.append(email)
    except Exception as e:
        logger.error(f"邮件通知初始化失败: {str(e)}")

    # TODO: 初始化其他通知方式（如企业微信等）

    logger.info("通知系统初始化成功")

def send_notification(message: Dict[str, Any]) -> bool:
    """
    发送通知

    Args:
        message (Dict[str, Any]): 通知消息

    Returns:
        bool: 是否至少有一个通知发送成功
    """
    logger = logging.getLogger(__name__)
    logger.info(f"收到通知消息: {message}")
    
    if not _notifiers:
        logger.warning("通知系统未初始化")
        return False
    
    success = False
    for notifier in _notifiers:
        try:
            if notifier.send(message):
                success = True
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}")
    
    return success 