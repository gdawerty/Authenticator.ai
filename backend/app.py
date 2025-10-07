import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from backend.config.config import Config
from backend.routes.main_routes import main_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.api_routes import api_bp
from backend.routes.parsing_routes import parsing_bp
from backend.routes.openai_classification_routes import openai_classification_bp
from backend.routes.authenticity_routes import authenticity_bp
from backend.routes.clone_search_routes import clone_search_bp
from backend.routes.stage3_clone_detection_routes import api as stage3_api
from backend.routes.ai_clone_detection_routes import ai_clone_routes
from backend.routes.cryptographic_validation_routes import crypto_validation_routes
from backend.routes.documents_routes import documents_bp

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
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(parsing_bp, url_prefix='/api')
    app.register_blueprint(openai_classification_bp)
    app.register_blueprint(authenticity_bp)
    app.register_blueprint(clone_search_bp, url_prefix='/api/clone')
    
    # Register AI clone detection routes
    app.register_blueprint(ai_clone_routes, url_prefix='/api')
    
    # Register cryptographic validation routes
    app.register_blueprint(crypto_validation_routes, url_prefix='/api')
    
    # Register documents routes
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    
    # Register the enhanced Stage 3 clone detection API
    from flask_restx import Api
    api = Api(app, doc='/api/stage3/doc/', version='1.0', title='Stage 3 Clone Detection API')
    api.add_namespace(stage3_api, path='/api/stage3')
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting Authenticator.ai Backend Server")
    with app.app_context():
        for rule in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
            methods = ', '.join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
            if methods:
                print(f"  {rule.rule:30s} [{methods}]")
    print("-" * 40 + "\n")
    
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
