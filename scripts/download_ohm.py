"""
下载 OpenHardwareMonitor DLL 文件
"""

import os
import sys
import requests
import zipfile
import shutil
from pathlib import Path

def download_ohm():
    """下载并解压 OpenHardwareMonitor"""
    
    # 创建临时目录
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # 下载 OpenHardwareMonitor
    url = "https://openhardwaremonitor.org/files/openhardwaremonitor-v0.9.6.zip"
    zip_path = temp_dir / "openhardwaremonitor.zip"
    
    print("正在下载 OpenHardwareMonitor...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        print(f"下载失败: {str(e)}")
        return False
    
    # 解压文件
    print("正在解压文件...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    except Exception as e:
        print(f"解压失败: {str(e)}")
        return False
    
    # 复制 DLL 文件
    dll_source = temp_dir / "OpenHardwareMonitor" / "OpenHardwareMonitorLib.dll"
    dll_target = Path("app/core/monitor/OpenHardwareMonitorLib.dll")
    
    print("正在复制 DLL 文件...")
    try:
        os.makedirs(os.path.dirname(dll_target), exist_ok=True)
        shutil.copy2(dll_source, dll_target)
        print(f"DLL 文件已复制到: {dll_target}")
    except Exception as e:
        print(f"复制 DLL 失败: {str(e)}")
        return False
    
    # 清理临时文件
    print("正在清理临时文件...")
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"清理临时文件失败: {str(e)}")
    
    return True

if __name__ == "__main__":
    if sys.platform != "win32":
        print("此脚本仅支持 Windows 系统")
        sys.exit(1)
        
    if download_ohm():
        print("OpenHardwareMonitor 安装成功")
    else:
        print("OpenHardwareMonitor 安装失败")
        sys.exit(1) 