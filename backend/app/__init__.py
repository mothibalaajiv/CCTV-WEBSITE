from flask import Flask
from flask_cors import CORS
from .config import Config
from .exceptions import register_error_handlers
from .extensions import jwt, swagger, init_mongo

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.url_map.strict_slashes = False

    # Initialize CORS
    cors_origins = app.config.get("CORS_ORIGINS", "*")
    if cors_origins != "*":
        cors_origins = [o.strip() for o in cors_origins.split(",") if o.strip()]
    CORS(app, resources={r"/api/*": {"origins": cors_origins}}, supports_credentials=True)

    # Initialize Extensions
    jwt.init_app(app)
    swagger.init_app(app)
    
    # Initialize MongoDB and optional admin sync
    with app.app_context():
        init_mongo(app)
        admin_pass = app.config.get("ADMIN_PASSWORD")
        if admin_pass:
            try:
                from app.repositories.user_repo import UserRepository
                from app.services.auth_service import AuthService
                admin_user = UserRepository.find_by_username("admin")
                if admin_user:
                    UserRepository.update(str(admin_user['_id']), {
                        "password_hash": AuthService.hash_password(admin_pass)
                    })
                else:
                    UserRepository.create({
                        "username": "admin",
                        "password_hash": AuthService.hash_password(admin_pass),
                        "role": "admin",
                        "assigned_sites": [],
                        "status": "active"
                    })
            except Exception as e:
                app.logger.warning(f"Admin password sync skipped: {e}")

    # Health check endpoints for Render and monitoring
    @app.route('/health', methods=['GET'])
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {"status": "ok", "service": "vms-backend"}, 200

    # Register Error Handlers
    register_error_handlers(app)

    # Register Blueprints
    from .api.auth_routes import auth_bp
    from .api.user_routes import user_bp
    from .api.site_routes import site_bp
    from .api.camera_routes import camera_bp
    from .api.stream_routes import stream_bp
    from .api.system_routes import system_bp

    from .api.server_routes import server_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(site_bp, url_prefix='/api/sites')
    app.register_blueprint(camera_bp, url_prefix='/api/cameras')
    app.register_blueprint(stream_bp, url_prefix='/api/streams')
    app.register_blueprint(system_bp, url_prefix='/api/system')
    app.register_blueprint(server_bp, url_prefix='/api/servers')
    
    from .api.public_routes import public_bp
    app.register_blueprint(public_bp, url_prefix='/api/public')
    
    return app
