from flask import Blueprint, jsonify

bp = Blueprint('notification', __name__)

@bp.route('/send', methods=['POST'])
def send_notification():
    """发送通知"""
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'status': 'sent'
        }
    }) 