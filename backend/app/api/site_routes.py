from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.site_service import SiteService
from app.utils.decorators import admin_required

site_bp = Blueprint('sites', __name__)

@site_bp.route('/', methods=['POST'])
@admin_required()
def create_site():
    """
    Create a new site (Admin Only)
    ---
    tags:
      - Sites
    """
    data = request.get_json()
    site = SiteService.create_site(data)
    return jsonify({"status": "success", "data": site}), 201

@site_bp.route('/', methods=['GET'])
@jwt_required()
def get_sites():
    """
    List all sites
    ---
    tags:
      - Sites
    """
    sites = SiteService.get_all_sites()
    return jsonify({"status": "success", "data": sites})

@site_bp.route('/<site_id>', methods=['PUT'])
@admin_required()
def update_site(site_id):
    data = request.get_json()
    SiteService.update_site(site_id, data)
    return jsonify({"status": "success", "message": "Site updated"})

@site_bp.route('/<site_id>', methods=['DELETE'])
@admin_required()
def delete_site(site_id):
    SiteService.delete_site(site_id)
    return jsonify({"status": "success", "message": "Site deleted"})
