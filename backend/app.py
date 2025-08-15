import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from backend.config.config import Config
from backend.routes.main_routes import main_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.api_routes import api_bp

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources=app.config['CORS_RESOURCES'])
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    
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
