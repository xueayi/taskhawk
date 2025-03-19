import time
import os
from app.core.monitor import start_monitors, stop_monitors
from app.core.utils.config import load_config

def main():
    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)
    
    # 加载配置
    config = load_config("config/config.yaml")
    
    # 确保配置中启用了日志监控
    if not config.get('check_log_enabled', False):
        print("警告：日志监控在配置中未启用")
        return
    
    # 启动监控
    print("启动监控...")
    start_monitors(config)
    
    # 等待5秒
    print("等待5秒...")
    time.sleep(5)
    
    # 写入测试日志
    print("写入测试日志...")
    with open(config['check_log_path'], "w", encoding="utf-8") as f:
        f.write("训练完成\n")
    
    # 等待10秒让监控检测到变化
    print("等待监控检测...")
    time.sleep(10)
    
    # 停止监控
    print("停止监控...")
    stop_monitors()

if __name__ == "__main__":
    main() 