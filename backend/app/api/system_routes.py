from flask import Blueprint, jsonify, request
from app.services.system_service import SystemService

system_bp = Blueprint('system', __name__)

@system_bp.route('/health', methods=['GET'])
def health_check():
    """
    System Health Check Endpoint
    ---
    tags:
      - Monitoring
    """
    return jsonify({"status": "healthy", "service": "VMS Backend API"})

@system_bp.route('/dashboard', methods=['GET'])
def dashboard_stats():
    """
    Dashboard Analytics Summary
    ---
    tags:
      - Dashboard
    """
    stats = SystemService.get_dashboard_stats()
    return jsonify({"status": "success", "data": stats})

@system_bp.route('/cloud-status', methods=['GET'])
def get_cloud_status():
    import os
    import requests
    cloud_url = os.environ.get('CLOUD_SERVER_URL', 'http://104.251.214.177:8000/api/streams')
    base_url = cloud_url.split('/api')[0]
    
    try:
        response = requests.get(f"{base_url}/api/diagnostics", timeout=3)
        if response.status_code == 200:
            return jsonify({"status": "success", "data": {"online": True}})
    except Exception:
        pass
        
    return jsonify({"status": "success", "data": {"online": False}})

@system_bp.route('/heartbeat', methods=['POST'])
def heartbeat():
    """
    Local Server Heartbeat
    ---
    tags:
      - Monitoring
    """
    data = request.get_json()
    result = SystemService.process_heartbeat(data.get('server_id'))
    return jsonify({"status": "success", "data": result})

from app.repositories.log_repo import MigrationRepository
from flask_jwt_extended import jwt_required

@system_bp.route('/camera-history', methods=['GET'])
@jwt_required()
def get_camera_history():
    history = MigrationRepository.find_all()
    for h in history:
        h['_id'] = str(h['_id'])
    return jsonify({"status": "success", "data": history})

@system_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    notifications = [
        {"id": "1", "type": "System", "message": "VMS Platform fully operational", "timestamp": "2026-06-18T10:00:00Z", "read": False}
    ]
    return jsonify({"status": "success", "data": notifications})

@system_bp.route('/search', methods=['GET'])
@jwt_required()
def global_search():
    query = request.args.get('q', '')
    if not query: return jsonify({"status": "success", "data": []})
    
    from app.repositories.camera_repo import CameraRepository
    from app.repositories.site_repo import SiteRepository
    cameras = CameraRepository.find_all()
    sites = SiteRepository.find_all()
    
    results = []
    for c in cameras:
        if query.lower() in str(c.get('camera_code', '')).lower() or query.lower() in str(c.get('location_name', '')).lower():
            results.append({"type": "camera", "title": f"Camera {c['camera_code']} - {c.get('location_name')}", "link": "/cameras"})
    for s in sites:
        if query.lower() in str(s.get('site_name', '')).lower() or query.lower() in str(s.get('site_id', '')).lower():
            results.append({"type": "site", "title": f"Site {s['site_id']} - {s.get('site_name')}", "link": "/sites"})
            
    return jsonify({"status": "success", "data": results})
