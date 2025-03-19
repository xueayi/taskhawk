"""
GPU 监控模块，支持 NVIDIA 和 AMD GPU
"""

import os
import time
import logging
import platform
import locale
from threading import Thread, Event
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# 创建 logger
logger = logging.getLogger(__name__)

def decode_bytes(byte_string: bytes) -> str:
    """
    解码字节串，尝试多种编码
    
    Args:
        byte_string: 要解码的字节串
    
    Returns:
        str: 解码后的字符串
    """
    encodings = ['utf-8', 'gbk', locale.getpreferredencoding(), 'ascii']
    
    for encoding in encodings:
        try:
            return byte_string.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    # 如果所有编码都失败，使用 'ignore' 选项的 utf-8
    return byte_string.decode('utf-8', errors='ignore')

class GPUMonitor:
    """GPU 监控类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化 GPU 监控器

        Args:
            config (Dict[str, Any]): 监控配置
        """
        self.config = config
        self.threshold = config.get('check_gpu_power_threshold', 50)  # 默认 50W
        self.consecutive_checks = config.get('check_gpu_power_consecutive_checks', 3)
        self.check_interval = config.get('check_interval', 5)
        self.enabled = config.get('check_gpu_power_enabled', False)
        self.stop_event = Event()
        self.monitor_thread: Optional[Thread] = None
        self.start_time = datetime.now()
        self.low_power_count = 0
        
        # 检测系统和可用的 GPU 工具
        self.os_type = platform.system()
        self.gpu_backend = self._detect_gpu_backend()
        self.gpu_ids = self._parse_gpu_ids(config.get('check_gpu_power_gpu_ids', 'all'))
        
        # 初始化 OpenHardwareMonitor（如果在 Windows 上）
        self.ohm = None
        if self.os_type == 'Windows' and self.gpu_backend == 'ohm':
            self._init_openhardwaremonitor()

    def _init_openhardwaremonitor(self):
        """初始化 OpenHardwareMonitor"""
        try:
            import clr
            import os
            ohm_path = os.path.join(os.path.dirname(__file__), 'OpenHardwareMonitorLib.dll')
            
            if not os.path.exists(ohm_path):
                logger.error(f"未找到 OpenHardwareMonitor DLL: {ohm_path}")
                return
            
            clr.AddReference(ohm_path)
            
            from OpenHardwareMonitor import Hardware
            
            self.ohm = Hardware.Computer()
            self.ohm.GPUEnabled = True
            self.ohm.Open()
            
            logger.info("OpenHardwareMonitor 初始化成功")
        except Exception as e:
            logger.error(f"初始化 OpenHardwareMonitor 失败: {str(e)}")
            self.ohm = None

    def _detect_gpu_backend(self) -> str:
        """
        检测可用的 GPU 监控后端

        Returns:
            str: 'nvidia', 'amd', 'ohm' 或 'none'
        """
        if self.os_type == 'Windows':
            try:
                # 尝试使用 OpenHardwareMonitor
                import clr
                logger.info("检测到 Windows 系统，尝试使用 OpenHardwareMonitor")
                return 'ohm'
            except ImportError:
                logger.warning("未找到 pythonnet 包，无法使用 OpenHardwareMonitor")
        
        try:
            # 尝试导入 NVIDIA 工具
            import pynvml
            pynvml.nvmlInit()
            logger.info("检测到 NVIDIA GPU，使用 NVML 接口")
            return 'nvidia'
        except:
            logger.debug("未找到 NVIDIA NVML 接口")

        try:
            if self.os_type == 'Linux':
                # 在 Linux 下检查 AMD GPU
                import pyamdgpuinfo
                if pyamdgpuinfo.detect_gpus() > 0:
                    logger.info("检测到 AMD GPU，使用 ROCm 接口")
                    return 'amd'
        except:
            logger.debug("未找到 AMD GPU 监控工具")

        logger.warning("未检测到支持的 GPU 或所需工具未安装")
        return 'none'

    def _get_gpu_info_ohm(self) -> List[Dict]:
        """获取 OpenHardwareMonitor GPU 信息"""
        if not self.ohm:
            return []
            
        try:
            gpu_info = []
            for i, hardware in enumerate(self.ohm.Hardware):
                if hardware.HardwareType == getattr(self.ohm.HardwareType, 'GpuAmd'):
                    hardware.Update()
                    
                    # 初始化数据
                    gpu_data = {
                        'id': i,
                        'name': hardware.Name,
                        'power': 0,
                        'temperature': 0,
                        'memory_used': 0,
                        'memory_total': 0,
                        'load': 0
                    }
                    
                    # 获取传感器数据
                    for sensor in hardware.Sensors:
                        if sensor.SensorType == getattr(self.ohm.SensorType, 'Power'):
                            gpu_data['power'] = sensor.Value
                        elif sensor.SensorType == getattr(self.ohm.SensorType, 'Temperature'):
                            gpu_data['temperature'] = sensor.Value
                        elif sensor.SensorType == getattr(self.ohm.SensorType, 'Load'):
                            if sensor.Name == 'GPU Core':
                                gpu_data['load'] = sensor.Value
                        elif sensor.SensorType == getattr(self.ohm.SensorType, 'Data'):
                            if 'Memory Used' in sensor.Name:
                                gpu_data['memory_used'] = sensor.Value
                            elif 'Memory Total' in sensor.Name:
                                gpu_data['memory_total'] = sensor.Value
                    
                    gpu_info.append(gpu_data)
                    logger.debug(
                        f"GPU {i} ({gpu_data['name']}) - "
                        f"功耗: {gpu_data['power']:.1f}W, "
                        f"温度: {gpu_data['temperature']}°C, "
                        f"负载: {gpu_data['load']}%, "
                        f"显存: {gpu_data['memory_used']:.0f}/{gpu_data['memory_total']:.0f}MB"
                    )
            
            return gpu_info
        except Exception as e:
            logger.error(f"获取 OpenHardwareMonitor GPU 信息失败: {str(e)}")
            return []

    def _get_nvidia_gpu_info(self) -> List[Dict]:
        """获取 NVIDIA GPU 信息"""
        try:
            import pynvml
            gpu_info = []
            device_count = pynvml.nvmlDeviceGetCount()
            
            for i in range(device_count):
                if i not in self.gpu_ids:
                    continue
                    
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                try:
                    name = pynvml.nvmlDeviceGetName(handle)
                    if isinstance(name, bytes):
                        name = decode_bytes(name)
                except Exception as e:
                    name = f"GPU-{i}"
                    logger.warning(f"获取 GPU {i} 名称失败: {str(e)}")

                try:
                    power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # 转换为瓦特
                except Exception as e:
                    power = 0
                    logger.warning(f"获取 GPU {i} 功耗失败: {str(e)}")

                try:
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                except Exception as e:
                    temp = 0
                    logger.warning(f"获取 GPU {i} 温度失败: {str(e)}")

                try:
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    memory_used = mem_info.used / 1024 / 1024  # 转换为 MB
                    memory_total = mem_info.total / 1024 / 1024
                except Exception as e:
                    memory_used = 0
                    memory_total = 0
                    logger.warning(f"获取 GPU {i} 内存信息失败: {str(e)}")
                
                gpu_info.append({
                    'id': i,
                    'name': name,
                    'power': power,
                    'temperature': temp,
                    'memory_used': memory_used,
                    'memory_total': memory_total
                })
                
                logger.info(f"GPU {i} ({name}) - 功耗: {power:.1f}W, 温度: {temp}°C")
            
            return gpu_info
        except Exception as e:
            logger.error(f"获取 NVIDIA GPU 信息失败: {str(e)}")
            return []

    def _get_amd_gpu_info(self) -> List[Dict]:
        """获取 AMD GPU 信息"""
        try:
            if self.os_type == 'Linux':
                import pyamdgpuinfo
                gpu_info = []
                
                for i in range(pyamdgpuinfo.detect_gpus()):
                    if i not in self.gpu_ids:
                        continue
                        
                    gpu = pyamdgpuinfo.get_gpu(i)
                    gpu_info.append({
                        'id': i,
                        'name': gpu.name,
                        'power': gpu.power_usage / 1000.0,  # 转换为瓦特
                        'temperature': gpu.temperature,
                        'memory_used': gpu.memory_usage,
                        'memory_total': gpu.memory_total
                    })
                
                return gpu_info
            else:
                # Windows 下使用 OpenHardwareMonitor
                import wmi
                w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                gpu_info = []
                
                for sensor in w.Sensor():
                    if sensor.SensorType == 'Power' and 'GPU' in sensor.Name:
                        gpu_id = int(sensor.Parent.split('GPU')[1])
                        if gpu_id not in self.gpu_ids:
                            continue
                            
                        gpu_info.append({
                            'id': gpu_id,
                            'name': sensor.Parent,
                            'power': sensor.Value,
                            'temperature': None,  # 需要单独查询
                            'memory_used': None,  # OpenHardwareMonitor 可能无法获取这些信息
                            'memory_total': None
                        })
                
                return gpu_info
        except Exception as e:
            logger.error(f"获取 AMD GPU 信息失败: {str(e)}")
            return []

    def _monitor_loop(self):
        """监控循环"""
        if self.gpu_backend == 'none':
            logger.error("未检测到支持的 GPU，停止监控")
            return

        while not self.stop_event.is_set():
            try:
                # 根据不同后端获取 GPU 信息
                if self.gpu_backend == 'nvidia':
                    gpu_info = self._get_nvidia_gpu_info()
                elif self.gpu_backend == 'amd':
                    gpu_info = self._get_amd_gpu_info()
                elif self.gpu_backend == 'ohm':
                    gpu_info = self._get_gpu_info_ohm()
                else:
                    logger.error("不支持的 GPU 类型")
                    return

                if not gpu_info:
                    logger.warning("未获取到 GPU 信息")
                    time.sleep(self.check_interval)
                    continue

                # 计算最大功耗
                powers = [gpu['power'] for gpu in gpu_info if gpu['power'] is not None]
                if not powers:
                    logger.warning("未获取到 GPU 功耗信息")
                    time.sleep(self.check_interval)
                    continue
                    
                max_power = max(powers)

                # 检查是否所有 GPU 功耗都低于阈值
                if max_power < self.threshold:
                    self.low_power_count += 1
                    logger.info(f"GPU 功耗低于阈值 ({self.threshold}W)，当前最大功耗: {max_power:.1f}W，连续次数: {self.low_power_count}/{self.consecutive_checks}")
                    
                    if self.low_power_count >= self.consecutive_checks:
                        end_time = datetime.now()
                        duration = end_time - self.start_time
                        logger.info(f"GPU 功耗连续 {self.consecutive_checks} 次低于阈值 {self.threshold}W")
                        logger.info(f"监控持续时间: {duration}")
                        
                        # 发送通知
                        self._send_notification(gpu_info, duration)
                        return
                else:
                    if self.low_power_count > 0:
                        logger.info(f"GPU 功耗恢复正常，重置计数器（最大功耗: {max_power:.1f}W）")
                    self.low_power_count = 0

            except Exception as e:
                logger.error(f"GPU 监控出错: {str(e)}")
            
            time.sleep(self.check_interval)

    def start(self):
        """启动 GPU 监控"""
        if not self.enabled:
            logger.info("GPU 功耗监控未启用")
            return

        logger.info(f"开始监控 GPU 功耗，阈值: {self.threshold}W，连续检查次数: {self.consecutive_checks}")
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        """停止 GPU 监控"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.stop_event.set()
            self.monitor_thread.join()
            logger.info("GPU 监控已停止")
            
        if self.ohm:
            self.ohm.Close()
            logger.info("OpenHardwareMonitor 已关闭")

    def _send_notification(self, gpu_info: List[Dict], duration):
        """发送通知"""
        try:
            from app.core.notification import send_notification
            
            # 构建 GPU 信息字符串
            gpu_details = []
            for gpu in gpu_info:
                details = [
                    f"GPU {gpu['id']} ({gpu['name']}):",
                    f"- 功耗: {gpu['power']:.1f}W",
                    f"- 温度: {gpu['temperature']}°C"
                ]
                
                if 'load' in gpu:
                    details.append(f"- 负载: {gpu['load']}%")
                    
                if gpu['memory_total'] > 0:
                    details.append(f"- 显存: {gpu['memory_used']:.0f}/{gpu['memory_total']:.0f}MB")
                
                gpu_details.append('\n'.join(details))
            
            message = {
                "title": "训练完成通知",
                "content": "GPU 功耗低于阈值，训练可能已完成\n\n" + "\n\n".join(gpu_details),
                "duration": str(duration),
                "method": "GPU 功耗监控",
                "project_name": self.config.get('project_name', '未知项目')
            }
            send_notification(message)
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}")

    def _parse_gpu_ids(self, gpu_ids: Union[str, List[int], int]) -> List[int]:
        """解析 GPU ID 配置"""
        try:
            if self.gpu_backend == 'ohm':
                # 对于 OpenHardwareMonitor，计算 AMD GPU 数量
                if not self.ohm:
                    return []
                max_gpus = sum(1 for h in self.ohm.Hardware 
                             if h.HardwareType == getattr(self.ohm.HardwareType, 'GpuAmd'))
            elif self.gpu_backend == 'nvidia':
                import pynvml
                max_gpus = pynvml.nvmlDeviceGetCount()
            elif self.gpu_backend == 'amd' and self.os_type == 'Linux':
                import pyamdgpuinfo
                max_gpus = pyamdgpuinfo.detect_gpus()
            else:
                max_gpus = 0
                logger.warning("无法检测 GPU 数量")
                return []

            if gpu_ids == 'all':
                gpu_list = list(range(max_gpus))
                logger.info(f"监控所有可用 GPU: {gpu_list}")
                return gpu_list
            elif isinstance(gpu_ids, int):
                if 0 <= gpu_ids < max_gpus:
                    logger.info(f"监控单个 GPU: {gpu_ids}")
                    return [gpu_ids]
            elif isinstance(gpu_ids, list):
                valid_ids = [i for i in gpu_ids if 0 <= i < max_gpus]
                if valid_ids:
                    logger.info(f"监控指定 GPU: {valid_ids}")
                    return valid_ids
            
            logger.warning(f"无效的 GPU ID 配置: {gpu_ids}，使用所有 GPU")
            return list(range(max_gpus))
        except Exception as e:
            logger.error(f"解析 GPU ID 时出错: {str(e)}")
            return [] 