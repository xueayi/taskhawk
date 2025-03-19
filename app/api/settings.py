from flask import Blueprint, request, jsonify
from app.core.utils.config import Config
from app.models.preset import Preset
from datetime import datetime

bp = Blueprint('settings', __name__)

@bp.route('/api/v1/settings', methods=['GET'])
def get_settings():
    """获取系统设置"""
    try:
        config = Config.get_instance()
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'settings': config.to_dict()
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        })

@bp.route('/api/v1/settings', methods=['POST'])
def update_settings():
    """更新系统设置"""
    try:
        data = request.get_json()
        config = Config.get_instance()
        config.update(data)
        config.save()
        
        return jsonify({
            'code': 200,
            'message': 'success'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        })

@bp.route('/api/v1/settings/presets', methods=['GET'])
def get_presets():
    """获取配置预设列表"""
    try:
        presets = Preset.find().sort('created_at', -1)
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'presets': [preset.to_dict() for preset in presets]
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        })

@bp.route('/api/v1/settings/presets', methods=['POST'])
def create_preset():
    """创建配置预设"""
    try:
        data = request.get_json()
        
        # 创建预设
        preset = Preset(
            name=data['name'],
            description=data.get('description', ''),
            settings=data['settings'],
            created_at=datetime.utcnow()
        )
        preset.save()
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'preset': preset.to_dict()
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        })

@bp.route('/api/v1/settings/presets/<preset_id>', methods=['GET'])
def get_preset(preset_id):
    """获取预设详情"""
    try:
        preset = Preset.find_one({'_id': preset_id})
        if not preset:
            return jsonify({
                'code': 404,
                'message': '预设不存在'
            })
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'preset': preset.to_dict()
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        })

@bp.route('/api/v1/settings/presets/<preset_id>', methods=['DELETE'])
def delete_preset(preset_id):
    """删除预设"""
    try:
        preset = Preset.find_one({'_id': preset_id})
        if not preset:
            return jsonify({
                'code': 404,
                'message': '预设不存在'
            })
        
        preset.delete()
        
        return jsonify({
            'code': 200,
            'message': 'success'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }) 