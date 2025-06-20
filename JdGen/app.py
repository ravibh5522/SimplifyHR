# ai_hr_jd_project/app.py
from flask import Flask, jsonify
from config import Config
from database.connection import init_db, SessionLocal # Import SessionLocal for teardown
from routes.jd_routes import jd_bp
from werkzeug.exceptions import HTTPException

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Cloud SQL connection pool and create tables
    # This should be called once when the application starts
    with app.app_context():
        init_db()

    # Register blueprints
    app.register_blueprint(jd_bp)

    # Teardown context to close DB connections
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if SessionLocal:
            SessionLocal.remove()

    # Generic error handler for HTTPExceptions (like abort(404))
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        response = e.get_response()
        response.data = jsonify({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }).data
        response.content_type = "application/json"
        return response

    # Generic error handler for other exceptions
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        # Log the error internally
        app.logger.error(f"An unhandled exception occurred: {e}", exc_info=True)
        # Return a generic error response
        response = jsonify({
            "code": 500,
            "name": "Internal Server Error",
            "description": "An unexpected error occurred on the server."
        })
        response.status_code = 500
        return response

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"}), 200

    return app

# If you want to run directly with `python app.py` for simple dev
if __name__ == '__main__':
     app = create_app()
     app.run(debug=True, host='0.0.0.0', port=5000)