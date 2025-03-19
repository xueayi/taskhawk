#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TaskNya - 任务监控与系统健康检测工具
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from app.core.utils.config import load_config
from app.core.utils.logger import setup_logger
from app.core.notification import init_notification

# 初始化Flask应用
app = Flask(__name__)
socketio = SocketIO(app)
db = SQLAlchemy()

def create_app(config_path=None):
    """
    创建Flask应用实例
        
        Args:
            config_path (str, optional): 配置文件路径
            
        Returns:
        Flask: Flask应用实例
    """
    # 加载配置
    config = load_config(config_path)
    
    # 设置Flask配置
    app.config['SECRET_KEY'] = config['app']['secret_key']
    app.config['SQLALCHEMY_DATABASE_URI'] = config['app']['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config['app']['SQLALCHEMY_TRACK_MODIFICATIONS']
    
    # 保存完整配置
    app.config.update(config)

    # 设置日志
    setup_logger(config['logging'])

    # 初始化通知系统
    init_notification(config)

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    from app.api.monitor import bp as monitor_bp
    from app.api.system import bp as system_bp
    from app.api.notification import bp as notification_bp
    
    app.register_blueprint(monitor_bp, url_prefix='/api/v1/monitor')
    app.register_blueprint(system_bp, url_prefix='/api/v1/system')
    app.register_blueprint(notification_bp, url_prefix='/api/v1/notification')

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app

def main():
    """
    主函数
    """
    import argparse
    parser = argparse.ArgumentParser(description="TaskNya - 任务监控与系统健康检测工具")
    parser.add_argument("--config", help="配置文件路径")
    args = parser.parse_args()
    
    # 创建应用
    app = create_app(args.config)

    # 启动监控服务
    from app.core.monitor import start_monitors
    if 'monitor' in app.config:
        start_monitors(app.config['monitor'])
    else:
        app.logger.warning("未找到监控配置，跳过启动监控服务")

    # 启动Web服务
    host = app.config['app']['host']
    port = app.config['app']['port']
    debug = False  # 禁用调试模式以避免重复加载
    
    socketio.run(app, host=host, port=port, debug=debug)
    exit()

if __name__ == "__main__":
    main()
