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
    CORS(app)

    # Initialize Extensions
    jwt.init_app(app)
    swagger.init_app(app)
    
    # Initialize MongoDB (requires app context or config)
    with app.app_context():
        init_mongo(app)

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
