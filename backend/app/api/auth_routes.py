from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.exceptions import APIError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User Login
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Successful login
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        raise APIError("Missing username or password", 400)
        
    result = AuthService.authenticate(data['username'], data['password'])
    return jsonify({"status": "success", "data": result})
