from flask import Blueprint, request, jsonify
from app.core.monitor import FileMonitor, LogMonitor, GPUMonitor
from app.models.task import Task
from app.core.utils.validators import validate_task_data
from datetime import datetime

bp = Blueprint('tasks', __name__)

@bp.route('/api/v1/tasks', methods=['GET'])
def get_tasks():
    """获取任务列表"""
    try:
        # 获取查询参数
        status = request.args.get('status')
        task_type = request.args.get('type')
        search = request.args.get('search')
        
        # 构建查询条件
        query = {}
        if status:
            query['status'] = status
        if task_type:
            query['type'] = task_type
        if search:
            query['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        
        # 查询任务列表
        tasks = Task.find(query).sort('created_at', -1)
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'tasks': [task.to_dict() for task in tasks]
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        })

@bp.route('/api/v1/tasks', methods=['POST'])
def create_task():
    """创建新任务"""
    try:
        data = request.get_json()
        
        # 验证任务数据
        if not validate_task_data(data):
            return jsonify({
                'code': 400,
                'message': '无效的任务数据'
            })
        
        # 创建任务实例
        task = Task(
            name=data['name'],
            type=data['type'],
            description=data.get('description', ''),
            settings=data.get('settings', {}),
            check_interval=int(data.get('check_interval', 5)),
            auto_stop=data.get('auto_stop', True),
            created_at=datetime.utcnow(),
            status='pending'
        )
        
        # 根据任务类型创建监控器
        if data['type'] == 'file':
            monitor = FileMonitor(
                file_path=data['settings']['file_path'],
                file_pattern=data['settings'].get('file_pattern', '*.*'),
                check_interval=task.check_interval
            )
        elif data['type'] == 'log':
            monitor = LogMonitor(
                log_path=data['settings']['log_path'],
                keywords=data['settings'].get('keywords', []),
                check_interval=task.check_interval
            )
        elif data['type'] == 'gpu':
            monitor = GPUMonitor(
                gpu_ids=data['settings'].get('gpu_ids', 'all'),
                power_threshold=float(data['settings'].get('power_threshold', 0)),
                temp_threshold=float(data['settings'].get('temp_threshold', 0)),
                check_interval=task.check_interval
            )
        else:
            return jsonify({
                'code': 400,
                'message': '不支持的任务类型'
            })
        
        # 保存任务
        task.save()
        
        # 启动监控
        monitor.start()
        task.update({'status': 'running', 'start_time': datetime.utcnow()})
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'task': task.to_dict()
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        })

@bp.route('/api/v1/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """获取任务详情"""
    try:
        task = Task.find_one({'_id': task_id})
        if not task:
            return jsonify({
                'code': 404,
                'message': '任务不存在'
            })
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'task': task.to_dict(include_metrics=True, include_logs=True)
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        })

@bp.route('/api/v1/tasks/<task_id>/stop', methods=['POST'])
def stop_task(task_id):
    """停止任务"""
    try:
        task = Task.find_one({'_id': task_id})
        if not task:
            return jsonify({
                'code': 404,
                'message': '任务不存在'
            })
        
        if task.status != 'running':
            return jsonify({
                'code': 400,
                'message': '任务未在运行'
            })
        
        # 停止监控
        if task.type == 'file':
            monitor = FileMonitor.get_instance(task_id)
        elif task.type == 'log':
            monitor = LogMonitor.get_instance(task_id)
        elif task.type == 'gpu':
            monitor = GPUMonitor.get_instance(task_id)
        
        if monitor:
            monitor.stop()
        
        # 更新任务状态
        task.update({
            'status': 'completed',
            'end_time': datetime.utcnow()
        })
        
        return jsonify({
            'code': 200,
            'message': 'success'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        })

@bp.route('/api/v1/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务"""
    try:
        task = Task.find_one({'_id': task_id})
        if not task:
            return jsonify({
                'code': 404,
                'message': '任务不存在'
            })
        
        # 如果任务正在运行，先停止它
        if task.status == 'running':
            if task.type == 'file':
                monitor = FileMonitor.get_instance(task_id)
            elif task.type == 'log':
                monitor = LogMonitor.get_instance(task_id)
            elif task.type == 'gpu':
                monitor = GPUMonitor.get_instance(task_id)
            
            if monitor:
                monitor.stop()
        
        # 删除任务
        task.delete()
        
        return jsonify({
            'code': 200,
            'message': 'success'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }) 