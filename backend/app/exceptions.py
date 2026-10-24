from flask import jsonify

class APIError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"status": "error", "message": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        import traceback
        traceback.print_exc()
        err_str = str(error)
        if "DNS" in err_str or "timeout" in err_str or "timed out" in err_str or "ConfigurationError" in err_str or "ServerSelection" in err_str:
            return jsonify({
                "status": "error", 
                "message": "Cannot connect to cloud database (MongoDB Atlas). Please check your internet connection."
            }), 503
        return jsonify({"status": "error", "message": "Server Error: " + err_str}), 500
