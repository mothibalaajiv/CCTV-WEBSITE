from app.repositories.server_repo import LocalServerRepository
from app.exceptions import APIError

class LocalServerService:
    @classmethod
    def register_server(cls, data):
        mac_address = data.get('mac_address')
        if not mac_address:
            raise APIError("MAC address is required", 400)
            
        all_servers = LocalServerRepository.find_all()
        
        # Check if MAC already exists
        for s in all_servers:
            if s.get('mac_address') == mac_address:
                raise APIError("MAC address already registered", 400)
                
        # Generate 2-series server_id
        max_id = 200000
        for s in all_servers:
            try:
                code = int(s.get('server_id', 0))
                if 200000 <= code < 300000 and code > max_id:
                    max_id = code
            except ValueError:
                pass
                
        new_server_id = str(max_id + 1)
        
        server_data = {
            "server_id": new_server_id,
            "mac_address": mac_address,
            "is_active": True
        }
        
        server = LocalServerRepository.create(server_data)
        server['_id'] = str(server['_id'])
        return server

    @classmethod
    def get_all_servers(cls):
        servers = LocalServerRepository.find_all()
        for s in servers:
            s['_id'] = str(s['_id'])
        return servers

    @classmethod
    def set_server_status(cls, id, is_active):
        updated = LocalServerRepository.update(id, {"is_active": is_active})
        if updated:
            updated['_id'] = str(updated['_id'])
        return updated

    @classmethod
    def delete_server(cls, id):
        LocalServerRepository.delete(id)
        return True
