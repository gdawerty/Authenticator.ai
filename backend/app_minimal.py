import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from backend.config.config import Config
from backend.routes.auth_routes import auth_bp
from backend.routes.documents_routes import documents_bp
from backend.routes.analysis_routes import analysis_bp

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Simple CORS configuration for development
    CORS(app, 
         origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:3000", "http://localhost:8000", "http://localhost:8080"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "Accept"])
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register essential blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.register_blueprint(analysis_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        return {
            "message": "Authenticator.AI Backend",
            "version": "1.0.0",
            "features": [
                "JWT Authentication",
                "OAuth (Google, Microsoft, GitHub, Discord)",
                "Document Upload & Management",
                "User Registration & Login"
            ]
        }
    
    @app.route('/health')
    def health():
        return {"status": "healthy", "service": "authenticator-ai"}
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
