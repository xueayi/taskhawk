import psutil
import GPUtil
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from .base_monitor import BaseMonitor

logger = logging.getLogger(__name__)

class SystemMonitor(BaseMonitor):
    """系统监控类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化系统监控器

        Args:
            config (Dict[str, Any]): 监控配置
        """
        super().__init__(config)
        self.metrics = {}
        self.warning_thresholds = {
            'cpu': config.get('cpu', {}).get('warning_threshold', 90),
            'memory': config.get('memory', {}).get('warning_threshold', 90),
            'disk': config.get('disk', {}).get('warning_threshold', 90),
            'gpu': config.get('gpu', {}).get('warning_threshold', 85),
            'gpu_temp': config.get('gpu', {}).get('temp_threshold', 80)
        }

    def start(self) -> None:
        """启动系统监控"""
        if not self.is_running:
            self.is_running = True
            logger.info("系统监控已启动")

    def stop(self) -> None:
        """停止系统监控"""
        if self.is_running:
            self.is_running = False
            logger.info("系统监控已停止")

    def check_status(self) -> Dict[str, Any]:
        """
        检查系统状态

        Returns:
            Dict[str, Any]: 系统状态信息
        """
        self.metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': self._get_cpu_info(),
            'memory': self._get_memory_info(),
            'disk': self._get_disk_info(),
            'network': self._get_network_info(),
            'gpu': self._get_gpu_info()
        }
        return self.metrics

    def _get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count()
        
        return {
            'usage': cpu_percent,
            'frequency': cpu_freq.current if cpu_freq else None,
            'cores': cpu_count,
            'warning': cpu_percent > self.warning_thresholds['cpu']
        }

    def _get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'warning': memory.percent > self.warning_thresholds['memory']
        }

    def _get_disk_info(self) -> Dict[str, Any]:
        """获取磁盘信息"""
        disk_info = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.mountpoint] = {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent,
                    'warning': usage.percent > self.warning_thresholds['disk']
                }
            except Exception as e:
                logger.error(f"获取磁盘信息失败: {str(e)}")
        return disk_info

    def _get_network_info(self) -> Dict[str, Any]:
        """获取网络信息"""
        network_info = {}
        net_io = psutil.net_io_counters()
        network_info['total'] = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
        
        # 获取各网络接口信息
        if self.config.get('network', {}).get('interfaces'):
            net_if = psutil.net_if_stats()
            for interface in self.config['network']['interfaces']:
                if interface in net_if:
                    network_info[interface] = {
                        'speed': net_if[interface].speed,
                        'mtu': net_if[interface].mtu,
                        'up': net_if[interface].isup
                    }
        return network_info

    def _get_gpu_info(self) -> Dict[str, Any]:
        """获取GPU信息"""
        try:
            gpus = GPUtil.getGPUs()
            gpu_info = []
            for gpu in gpus:
                info = {
                    'id': gpu.id,
                    'name': gpu.name,
                    'load': gpu.load * 100,
                    'memory': {
                        'total': gpu.memoryTotal,
                        'used': gpu.memoryUsed,
                        'free': gpu.memoryFree,
                        'percent': (gpu.memoryUsed / gpu.memoryTotal) * 100
                    },
                    'temperature': gpu.temperature,
                    'warning': {
                        'temp': gpu.temperature > self.warning_thresholds['gpu_temp'],
                        'usage': gpu.load * 100 > self.warning_thresholds['gpu']
                    }
                }
                gpu_info.append(info)
            return gpu_info
        except Exception as e:
            logger.error(f"获取GPU信息失败: {str(e)}")
            return []

    def get_warnings(self) -> List[Dict[str, Any]]:
        """
        获取警告信息

        Returns:
            List[Dict[str, Any]]: 警告信息列表
        """
        warnings = []
        
        # CPU警告
        if self.metrics.get('cpu', {}).get('warning'):
            warnings.append({
                'type': 'cpu',
                'message': f"CPU使用率过高: {self.metrics['cpu']['usage']}%",
                'threshold': self.warning_thresholds['cpu'],
                'value': self.metrics['cpu']['usage']
            })
            
        # 内存警告
        if self.metrics.get('memory', {}).get('warning'):
            warnings.append({
                'type': 'memory',
                'message': f"内存使用率过高: {self.metrics['memory']['percent']}%",
                'threshold': self.warning_thresholds['memory'],
                'value': self.metrics['memory']['percent']
            })
            
        # 磁盘警告
        for mount_point, info in self.metrics.get('disk', {}).items():
            if info.get('warning'):
                warnings.append({
                    'type': 'disk',
                    'message': f"磁盘使用率过高 ({mount_point}): {info['percent']}%",
                    'threshold': self.warning_thresholds['disk'],
                    'value': info['percent']
                })
                
        # GPU警告
        for gpu in self.metrics.get('gpu', []):
            if gpu['warning']['temp']:
                warnings.append({
                    'type': 'gpu_temperature',
                    'message': f"GPU {gpu['id']} 温度过高: {gpu['temperature']}°C",
                    'threshold': self.warning_thresholds['gpu_temp'],
                    'value': gpu['temperature']
                })
            if gpu['warning']['usage']:
                warnings.append({
                    'type': 'gpu_usage',
                    'message': f"GPU {gpu['id']} 使用率过高: {gpu['load']}%",
                    'threshold': self.warning_thresholds['gpu'],
                    'value': gpu['load']
                })
                
        return warnings 