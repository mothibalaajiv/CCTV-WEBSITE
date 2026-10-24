import os
import json
import urllib.request
from datetime import datetime, timezone, timedelta
from app.extensions import db

def parse_timestamp(ts):
    if not ts:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)

def is_telemetry_fresh(d_time, now_utc=None, max_cloud_ts=None, window_seconds=300):
    """
    Determines whether a telemetry timestamp is fresh.
    Handles clock skew and timezone offsets (e.g., IST UTC+5:30 = 19800 seconds).
    """
    if not d_time or d_time == datetime.min.replace(tzinfo=timezone.utc):
        return False
        
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)
        
    diff = (now_utc - d_time).total_seconds()
    
    # 1. Direct match (allowing up to 60s slight future drift)
    if -60 <= diff <= window_seconds:
        return True
        
    # 2. Timezone offset compensation (e.g. IST UTC+5:30)
    for offset_hours in [5.5, -5.5]:
        offset_sec = offset_hours * 3600
        skewed_diff = diff - offset_sec
        if -60 <= skewed_diff <= window_seconds:
            return True

    # 3. Relative freshness to newest telemetry received from this server
    if max_cloud_ts and max_cloud_ts != datetime.min.replace(tzinfo=timezone.utc):
        max_diff = (now_utc - max_cloud_ts).total_seconds()
        for offset_hours in [0, 5.5, -5.5]:
            if -60 <= (max_diff - offset_hours * 3600) <= window_seconds:
                rel_diff = abs((max_cloud_ts - d_time).total_seconds())
                if rel_diff <= window_seconds:
                    return True
            
    return False

def fetch_cloud_diagnostics():
    """
    Fetches diagnostic telemetry from cloud server, falling back to MongoDB's
    diagnostics collection if the cloud endpoint is unreachable or empty.
    """
    cloud_url = os.getenv("CLOUD_SERVER_URL", "http://104.251.214.177:8000/api/diagnostics")
    if cloud_url.endswith("/api/streams"):
        cloud_url = cloud_url.replace("/api/streams", "/api/diagnostics")
        
    cloud_data = []
    try:
        req = urllib.request.Request(cloud_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3.0) as response:
            cloud_data = json.loads(response.read().decode()).get('data', [])
    except Exception:
        cloud_data = []
        
    # If cloud endpoint returned nothing, check MongoDB diagnostics collection directly
    if not cloud_data and db is not None:
        try:
            mongo_diags = list(db.get_collection('diagnostics').find())
            for md in mongo_diags:
                if '_id' in md:
                    md['_id'] = str(md['_id'])
                cloud_data.append(md)
        except Exception:
            pass
            
    return cloud_data

def camera_matches(cam_dict, target_mac, target_code=None):
    """
    Checks if a camera matches target_mac or target_code, checking mac_address,
    mac_aliases, and camera_code case-insensitively.
    """
    t_mac = (target_mac or '').lower().strip()
    t_code = str(target_code or '').strip()
    
    c_mac = (cam_dict.get('mac_address') or cam_dict.get('camera_mac') or '').lower().strip()
    c_code = str(cam_dict.get('camera_code') or '').strip()
    
    if t_mac and c_mac == t_mac:
        return True
        
    aliases = [(a or '').lower().strip() for a in cam_dict.get('mac_aliases', [])]
    if t_mac and t_mac in aliases:
        return True
        
    if t_code and c_code and t_code == c_code:
        return True
        
    return False
