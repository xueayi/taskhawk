from flask import Blueprint, jsonify

bp = Blueprint('monitor', __name__)

@bp.route('/status', methods=['GET'])
def get_status():
    """获取监控状态"""
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'status': 'running'
        }
    }) 