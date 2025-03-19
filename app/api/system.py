from flask import Blueprint, jsonify

bp = Blueprint('system', __name__)

@bp.route('/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'status': 'running'
        }
    }) 