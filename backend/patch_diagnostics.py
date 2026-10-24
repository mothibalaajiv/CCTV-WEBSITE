import os

file_path = r"D:\CCTV-LOCALSERVER\local_agent\monitoring\diagnostics_service.py"

with open(file_path, "r") as f:
    content = f.read()

content = content.replace(
    'hasattr(stream_pusher, "processes") and mac_clean in stream_pusher.processes:', 
    'hasattr(stream_pusher, "active_processes") and mac_clean in stream_pusher.active_processes:'
)
content = content.replace(
    'proc = stream_pusher.processes[mac_clean]', 
    'proc = stream_pusher.active_processes[mac_clean]'
)

content = content.replace(
    'hasattr(local_recorder, "processes") and mac_clean in local_recorder.processes:', 
    'hasattr(local_recorder, "active_processes") and mac_clean in local_recorder.active_processes:'
)
content = content.replace(
    'proc = local_recorder.processes[mac_clean]', 
    'proc = local_recorder.active_processes[mac_clean]'
)

with open(file_path, "w") as f:
    f.write(content)

print("Patch applied successfully.")
