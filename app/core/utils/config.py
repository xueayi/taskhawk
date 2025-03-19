"""
配置加载模块
"""

import os
import yaml
import logging
from typing import Dict, Any

# 默认配置
DEFAULT_CONFIG = {
    'app': {
        'name': 'TaskNya',
        'host': '0.0.0.0',
        'port': 15000,
        'debug': False,
        'secret_key': 'your-secret-key',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///tasknya.db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    },
    'monitor': {
        'project_name': '深度学习训练',
        'check_interval': 5,
        'logprint': 60,
        'timeout': None,
        'check_file_enabled': True,
        'check_file_path': './output/model_final.pth',
        'check_log_enabled': False,
        'check_log_path': './logs/training.log',
        'check_log_markers': [
            'Training completed',
            '任务完成',
            '训练完成',
            'Epoch [300/300]'
        ],
        'check_gpu_power_enabled': False,
        'check_gpu_power_threshold': 50.0,
        'check_gpu_power_gpu_ids': 'all',
        'check_gpu_power_consecutive_checks': 3,
        'system': {
            'enabled': True,
            'interval': 5,
            'cpu': {
                'enabled': True,
                'warning_threshold': 90
            },
            'memory': {
                'enabled': True,
                'warning_threshold': 90
            },
            'disk': {
                'enabled': True,
                'warning_threshold': 90
            },
            'gpu': {
                'enabled': True,
                'warning_threshold': 85,
                'temp_threshold': 80
            },
            'network': {
                'enabled': True,
                'interfaces': ['eth0', 'wlan0']
            }
        }
    },
    'logging': {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'logs/tasknya.log',
        'max_size': 10485760,
        'backup_count': 5,
        'encoding': 'utf-8'
    }
}

def deep_update(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    递归更新字典

    Args:
        base_dict (Dict[str, Any]): 基础字典
        update_dict (Dict[str, Any]): 更新字典

    Returns:
        Dict[str, Any]: 更新后的字典
    """
    for key, value in update_dict.items():
        if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
            base_dict[key] = deep_update(base_dict[key], value)
        else:
            base_dict[key] = value
    return base_dict

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    加载配置文件

    Args:
        config_path (str, optional): 配置文件路径. Defaults to None.

    Returns:
        Dict[str, Any]: 配置字典
    """
    config = DEFAULT_CONFIG.copy()
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    config = deep_update(config, user_config)
        except Exception as e:
            logging.error(f"加载配置文件失败: {str(e)}")
            logging.warning("使用默认配置")
    else:
        logging.warning("配置文件不存在，使用默认配置")
    
    return config

def validate_config(config: Dict[str, Any]) -> bool:
    """
    验证配置是否有效

    Args:
        config (Dict[str, Any]): 配置信息

    Returns:
        bool: 配置是否有效
    """
    # TODO: 实现配置验证逻辑
    return True 