import time
import os
import sys
import locale
import logging
from app.core.monitor import start_monitors, stop_monitors
from app.core.utils.config import load_config
from app.core.monitor.gpu_monitor import GPUMonitor

def setup_encoding():
    """设置正确的编码"""
    # 获取系统默认编码
    system_encoding = locale.getpreferredencoding()
    
    # 设置环境变量
    if system_encoding.upper() != 'UTF-8':
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # 设置标准输出编码
    if sys.stdout.encoding != 'utf-8':
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        else:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

def setup_logging():
    """配置日志系统"""
    # 确保日志目录存在
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, 'gpu_monitor_test.log')
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )

def main():
    # 设置编码
    setup_encoding()
    
    # 设置日志
    setup_logging()
    
    # 加载配置
    config = {
        'project_name': '测试项目',
        'check_interval': 5,  # 缩短检查间隔以便测试
        
        # GPU 监控配置
        'check_gpu_power_enabled': True,
        'check_gpu_power_threshold': 50,  # 设置较高的阈值以便触发
        'check_gpu_power_gpu_ids': 'all',
        'check_gpu_power_consecutive_checks': 3,  # 缩短连续检查次数以便测试
        
        # 其他监控配置（禁用）
        'check_file_enabled': False,
        'check_log_enabled': False
    }
    
    logger = logging.getLogger(__name__)
    
    try:
        # 启动监控
        logger.info("启动监控...")
        monitor = GPUMonitor(config)
        monitor.start()
        
        # 等待30秒让监控检测
        logger.info("等待监控检测（30秒）...")
        time.sleep(30)
        
    except Exception as e:
        logger.error(f"监控过程中出错: {str(e)}")
    finally:
        # 停止监控
        logger.info("停止监控...")
        stop_monitors()

if __name__ == "__main__":
    main() 