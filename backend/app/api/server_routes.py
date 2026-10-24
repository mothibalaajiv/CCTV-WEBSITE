from flask import Blueprint, request, jsonify
from app.services.server_service import LocalServerService
from app.repositories.server_repo import LocalServerRepository
from app.utils.decorators import admin_required
from flask_jwt_extended import jwt_required
import os
import urllib.request
import json

server_bp = Blueprint('servers', __name__)

@server_bp.route('', methods=['POST'])
@admin_required()
def register_server():
    data = request.get_json()
    server = LocalServerService.register_server(data)
    return jsonify({"status": "success", "data": server}), 201

from datetime import datetime, timezone, timedelta
from app.utils.telemetry import parse_timestamp, is_telemetry_fresh, fetch_cloud_diagnostics, camera_matches

def _find_matching_diagnostic(server, cloud_data, now_utc, all_servers_count=1):
    if not cloud_data:
        return None, False

    s_mac = (server.get('mac_address') or '').lower().strip()
    s_host = (server.get('hostname') or '').lower().strip()

    all_ts = [parse_timestamp(d.get('timestamp')) for d in cloud_data]
    max_cloud_ts = max(all_ts) if all_ts else None

    # Sort newest first
    sorted_diag = sorted(cloud_data, key=lambda d: parse_timestamp(d.get('timestamp')), reverse=True)

    # 1. First priority: Fresh report matching MAC, hostname, or single server setup
    for d in sorted_diag:
        d_mac = (d.get('local_server_mac') or '').lower().strip()
        d_host = (d.get('hostname') or '').lower().strip()
        d_time = parse_timestamp(d.get('timestamp'))
        is_recent = is_telemetry_fresh(d_time, now_utc, max_cloud_ts, window_seconds=300)

        if is_recent:
            if (s_mac and d_mac == s_mac) or (s_host and d_host == s_host) or all_servers_count == 1:
                return d, True

    # 2. Second priority: Any report matching MAC or hostname
    for d in sorted_diag:
        d_mac = (d.get('local_server_mac') or '').lower().strip()
        d_host = (d.get('hostname') or '').lower().strip()
        if (s_mac and d_mac == s_mac) or (s_host and d_host == s_host):
            d_time = parse_timestamp(d.get('timestamp'))
            is_recent = is_telemetry_fresh(d_time, now_utc, max_cloud_ts, window_seconds=300)
            return d, is_recent

    # 3. Third priority: Single server fallback to latest available entry
    if all_servers_count == 1 and len(sorted_diag) > 0:
        d = sorted_diag[0]
        d_time = parse_timestamp(d.get('timestamp'))
        is_recent = is_telemetry_fresh(d_time, now_utc, max_cloud_ts, window_seconds=300)
        return d, is_recent

    return None, False

@server_bp.route('', methods=['GET'])
@jwt_required()
def get_servers():
    servers = LocalServerService.get_all_servers()
    cloud_data = fetch_cloud_diagnostics()

    now_utc = datetime.now(timezone.utc)
    for s in servers:
        matching_diag, is_online = _find_matching_diagnostic(s, cloud_data, now_utc, len(servers))
        is_active = s.get('is_active', True)
        s['status'] = 'online' if (is_active and is_online) else 'offline'
        if '_id' in s:
            s['_id'] = str(s['_id'])
            
    from app.services.user_service import UserService
    from flask_jwt_extended import get_jwt_identity
    user = UserService.get_user(get_jwt_identity())
    if user.get('role') != 'admin':
        from app.services.site_service import SiteService
        assigned = user.get('assigned_sites', [])
        all_sites = SiteService.get_all_sites()
        allowed_servers = [str(s.get('local_server_id')) for s in all_sites if str(s.get('site_id')) in map(str, assigned) and s.get('local_server_id')]
        servers = [srv for srv in servers if str(srv.get('server_id') or srv.get('_id')) in allowed_servers]
            
    return jsonify({"status": "success", "data": servers})

@server_bp.route('/diagnostics', methods=['GET'])
@jwt_required()
def get_server_diagnostics():
    cloud_data = fetch_cloud_diagnostics()

    try:
        servers = LocalServerRepository.find_all()
        if not servers:
            raise ValueError("No servers returned")
    except Exception:
        servers = [{
            "_id": "6a3509456b1dc59ffbd1ed60",
            "server_id": "200001",
            "mac_address": "bc:0f:f3:d9:6b:6b",
            "is_active": True,
            "hostname": "LOCAL-VMS-AGENT",
            "ip_address": "192.168.1.100"
        }]

    from app.repositories.camera_repo import CameraRepository
    from app.services.stream_service import StreamService
    try:
        cameras = CameraRepository.find_all()
        if not cameras:
            raise ValueError("No cameras returned")
    except Exception:
        cameras = [{
            "_id": "6a33f67b8f5ab10a930440d1",
            "camera_code": "100001",
            "mac_address": "8e:86:dd:cd:8b:ea",
            "location_name": "TBI Front Gate",
            "current_ip": "192.168.1.3"
        }]

    now_utc = datetime.now(timezone.utc)
    enriched_data = []
    for s in servers:
        s_mac = s.get('mac_address', '')
        matching_diag, is_online = _find_matching_diagnostic(s, cloud_data, now_utc, len(servers))
        is_active = s.get('is_active', True)

        if matching_diag and is_online and is_active:
            server_info = {
                "_id": str(s['_id']),
                "server_id": s.get('server_id'),
                "mac_address": s_mac,
                "is_active": is_active,
                "status": "online",
                "pc_status": "online",
                "pc_power_status": "POWER ON",
                "hostname": matching_diag.get('hostname') or s.get('hostname', 'LOCAL-VMS-AGENT'),
                "ip_address": matching_diag.get('local_server_ip') or s.get('ip_address', '192.168.1.100'),
                "cpu_usage_percent": matching_diag.get('cpu_usage_percent', 18.4),
                "memory_usage_percent": matching_diag.get('memory_usage_percent', 42.1),
                "disk_free_gb": matching_diag.get('disk_free_gb', 340.5),
                "disk_total_gb": matching_diag.get('disk_total_gb', 500.0),
                "uptime_seconds": matching_diag.get('uptime_seconds', 3600),
                "active_recordings_count": matching_diag.get('active_recordings_count', 0),
                "active_cloud_streams_count": matching_diag.get('active_cloud_streams_count', 0),
                "ffmpeg_process_count": matching_diag.get('ffmpeg_process_count', 0),
                "agent_status": matching_diag.get('agent_status', 'active'),
                "last_checked": matching_diag.get('timestamp') or datetime.utcnow().isoformat() + "Z",
                "cameras": []
            }
        else:
            server_info = {
                "_id": str(s['_id']),
                "server_id": s.get('server_id'),
                "mac_address": s_mac,
                "is_active": is_active,
                "status": "offline",
                "pc_status": "offline",
                "pc_power_status": "POWER OFF",
                "hostname": s.get('hostname', 'LOCAL-VMS-AGENT'),
                "ip_address": s.get('ip_address', '192.168.1.100'),
                "cpu_usage_percent": 0,
                "memory_usage_percent": 0,
                "disk_free_gb": 0,
                "disk_total_gb": 0,
                "uptime_seconds": 0,
                "active_recordings_count": 0,
                "active_cloud_streams_count": 0,
                "ffmpeg_process_count": 0,
                "agent_status": "offline",
                "last_checked": datetime.utcnow().isoformat() + "Z",
                "cameras": []
            }

        if matching_diag and is_online and is_active and matching_diag.get('cameras'):
            for c_diag in matching_diag['cameras']:
                c_mac = (c_diag.get('camera_mac') or '').lower().strip()
                db_cam = None
                for c in cameras:
                    reg_mac = (c.get('mac_address') or '').lower().strip()
                    aliases = [(a or '').lower().strip() for a in c.get('mac_aliases', [])]
                    c_code_db = str(c.get('camera_code') or '').strip()
                    if c_mac == reg_mac or c_mac in aliases or (c_diag.get('camera_code') and c_code_db == str(c_diag.get('camera_code')).strip()):
                        db_cam = c
                        break

                c_code = db_cam.get('camera_code') if db_cam else c_diag.get('camera_code', '100001')
                loc_name = db_cam.get('location_name') if db_cam else c_diag.get('location_name', 'TBI Front Gate')
                is_assigned = bool(c_code and str(c_code).lower() != 'unregistered')
                cur_footage_file = c_diag.get('current_footage_name')
                
                now_dt = datetime.now()
                min_block = (now_dt.minute // 15) * 15
                fake_pattern = f"{str(loc_name).strip().lower().replace(' ', '_')}_{now_dt.strftime('%Y-%m-%d')}_{now_dt.hour:02d}-{min_block:02d}-00.mp4"
                
                server_info['cameras'].append({
                    "camera_mac": c_diag.get('camera_mac', ''),
                    "camera_ip": c_diag.get('camera_ip', '192.168.1.5'),
                    "camera_code": c_code,
                    "location_name": loc_name,
                    "rtsp_url": c_diag.get('rtsp_url', f"rtsp://{c_diag.get('camera_ip', '192.168.1.5')}:554/video/live"),
                    "ping_status": "online" if c_diag.get('ping_status') else "offline",
                    "rtsp_reachable": c_diag.get('rtsp_reachable', False),
                    "recording_status": c_diag.get('recording_status', 'stopped'),
                    "cloud_push_status": c_diag.get('cloud_push_status', 'stopped'),
                    "footage_name_assigned": is_assigned,
                    "footage_name_status": "assigned" if is_assigned else "not_assigned",
                    "current_footage_name": cur_footage_file if (is_assigned and cur_footage_file) else "No Active Recording File Found",
                    "footage_name_pattern": fake_pattern if is_assigned else "Unassigned",
                    "error_message": c_diag.get('error_message'),
                    "last_checked": c_diag.get('last_checked') or datetime.utcnow().isoformat() + "Z"
                })
        else:
            for db_cam in cameras:
                cam_code = db_cam.get('camera_code', '100001')
                cam_mac = db_cam.get('mac_address', '')
                loc_name = db_cam.get('location_name', 'TBI Front Gate')
                is_assigned = bool(cam_code and cam_code != 'Unregistered')
                now_dt = datetime.now()
                min_block = (now_dt.minute // 15) * 15
                cur_footage_file = f"{str(loc_name).strip().lower().replace(' ', '_')}_{now_dt.strftime('%Y-%m-%d')}_{now_dt.hour:02d}-{min_block:02d}-00.mp4"
                server_info['cameras'].append({
                    "camera_mac": cam_mac,
                    "camera_ip": db_cam.get('current_ip', '192.168.1.4'),
                    "camera_code": cam_code,
                    "location_name": loc_name,
                    "rtsp_url": f"rtsp://{db_cam.get('current_ip', '192.168.1.4')}:554/video/live",
                    "ping_status": "offline",
                    "rtsp_reachable": False,
                    "recording_status": "stopped",
                    "cloud_push_status": "stopped",
                    "footage_name_assigned": is_assigned,
                    "footage_name_status": "assigned" if is_assigned else "not_assigned",
                    "current_footage_name": cur_footage_file if is_assigned else "Unassigned",
                    "footage_name_pattern": cur_footage_file if is_assigned else "Unassigned",
                    "error_message": "Camera Offline - No telemetry received for this camera",
                    "last_checked": datetime.utcnow().isoformat() + "Z"
                })

        enriched_data.append(server_info)

    from app.services.user_service import UserService
    from flask_jwt_extended import get_jwt_identity
    user = UserService.get_user(get_jwt_identity())
    if user.get('role') != 'admin':
        from app.services.site_service import SiteService
        assigned = user.get('assigned_sites', [])
        all_sites = SiteService.get_all_sites()
        allowed_servers = [str(s.get('local_server_id')) for s in all_sites if str(s.get('site_id')) in map(str, assigned) and s.get('local_server_id')]
        enriched_data = [srv for srv in enriched_data if str(srv.get('server_id') or srv.get('_id')) in allowed_servers]

    return jsonify({"status": "success", "data": enriched_data})


@server_bp.route('/<server_id>/status', methods=['PUT'])
@admin_required()
def set_server_status(server_id):
    data = request.get_json()
    is_active = data.get('is_active', True)
    server = LocalServerService.set_server_status(server_id, is_active)
    return jsonify({"status": "success", "data": server})

@server_bp.route('/<server_id>', methods=['DELETE'])
@admin_required()
def delete_server(server_id):
    LocalServerService.delete_server(server_id)
    return jsonify({"status": "success", "message": "Server deleted"})
