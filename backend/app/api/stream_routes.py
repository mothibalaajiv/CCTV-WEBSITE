from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.stream_service import StreamService
from app.utils.decorators import admin_required

stream_bp = Blueprint('streams', __name__)

@stream_bp.route('/', methods=['GET'])
@jwt_required()
def get_streams():
    """
    List all active/inactive streams
    ---
    tags:
      - Streams
    """
    streams = StreamService.get_all_streams()
    return jsonify({"status": "success", "data": streams})

@stream_bp.route('/pause', methods=['POST'])
@admin_required()
def pause_stream():
    """
    Pause a live stream
    ---
    tags:
      - Streams
    """
    data = request.get_json()
    stream = StreamService.pause_stream(data['camera_code'])
    return jsonify({"status": "success", "data": stream})

@stream_bp.route('/resume', methods=['POST'])
@admin_required()
def resume_stream():
    """
    Resume a live stream
    ---
    tags:
      - Streams
    """
    data = request.get_json()
    stream = StreamService.resume_stream(data['camera_code'])
    return jsonify({"status": "success", "data": stream})
