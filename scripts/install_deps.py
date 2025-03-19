import os
import sys
import subprocess
import platform

def install_requirements():
    """安装项目依赖"""
    try:
        # 确保 pip 是最新的
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # 读取 requirements.txt
        with open("requirements.txt", "r", encoding="utf-8") as f:
            requirements = f.read()
        
        # 将依赖写入临时文件
        temp_req = "temp_requirements.txt"
        with open(temp_req, "w", encoding="utf-8") as f:
            f.write(requirements)
        
        # 安装依赖
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", temp_req])
        
        # 清理临时文件
        os.remove(temp_req)
        
        print("依赖安装完成！")
        
    except Exception as e:
        print(f"安装过程中出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # 创建 scripts 目录
    os.makedirs("scripts", exist_ok=True)
    
    # 安装依赖
    install_requirements() 