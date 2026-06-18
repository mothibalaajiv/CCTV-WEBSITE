from app.repositories.site_repo import SiteRepository
from app.services.user_service import UserService
from app.exceptions import APIError

class SiteService:
    @classmethod
    def check_server_mapping(cls, server_id, exclude_site_id=None):
        if not server_id:
            return
        sites = SiteRepository.find_all()
        for s in sites:
            if s.get('local_server_id') == server_id and s.get('site_id') != exclude_site_id:
                raise APIError(f"Local Server {server_id} is already mapped to site {s.get('site_id')}", 400)

    @classmethod
    def create_site(cls, data):
        if SiteRepository.find_by_site_id(data['site_id']):
            raise APIError("Site ID already exists", 400)
            
        cls.check_server_mapping(data.get('local_server_id'))
            
        site_data = {
            "site_id": data['site_id'],
            "site_name": data['site_name'],
            "local_server_id": data.get('local_server_id'),
            "status": data.get('status', 'active')
        }
        
        site = SiteRepository.create(site_data)
        site['_id'] = str(site['_id'])
        
        # Assign user
        assigned_user = data.get('assigned_user')
        if assigned_user:
            user = UserService.get_user(assigned_user)
            if user:
                sites = user.get('assigned_sites', [])
                if data['site_id'] not in sites:
                    sites.append(data['site_id'])
                    UserService.update_user(assigned_user, {"assigned_sites": sites})
        
        return site

    @classmethod
    def get_all_sites(cls):
        sites = SiteRepository.find_all()
        for s in sites:
            s['_id'] = str(s['_id'])
        return sites

    @classmethod
    def update_site(cls, site_id, data):
        site = SiteRepository.find_by_id(site_id)
        if not site:
            raise APIError("Site not found", 404)
        
        update_data = {}
        if 'site_name' in data: update_data['site_name'] = data['site_name']
        if 'local_server_id' in data:
            cls.check_server_mapping(data['local_server_id'], site['site_id'])
            update_data['local_server_id'] = data['local_server_id']
            
        if 'status' in data: update_data['status'] = data['status']
        
        SiteRepository.update(site_id, update_data)
        return True

    @classmethod
    def delete_site(cls, site_id):
        site = SiteRepository.find_by_id(site_id)
        if not site:
            raise APIError("Site not found", 404)
        SiteRepository.delete(site_id)
        return True
