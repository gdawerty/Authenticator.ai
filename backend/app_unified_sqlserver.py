"""
Unified Authenticator.AI Backend - SQL Server Version
Enhanced backend with SQL Server integration for production deployment
"""

import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from backend.config.config import Config

# Import SQL Server route blueprints
from backend.routes.auth_routes_sqlserver import auth_bp
from backend.routes.analysis_routes_sqlserver import analysis_bp

# Import existing route modules that don't need SQL Server changes
try:
    from backend.routes.main_routes import main_bp
except ImportError:
    main_bp = None

try:
    from backend.routes.api_routes import api_bp
except ImportError:
    api_bp = None

try:
    from backend.routes.parsing_routes import parsing_bp
except ImportError:
    parsing_bp = None

try:
    from backend.routes.cryptographic_validation_routes import crypto_validation_routes
except ImportError:
    crypto_validation_routes = None

try:
    from backend.routes.ai_clone_detection_routes import ai_clone_routes
except ImportError:
    ai_clone_routes = None

try:
    from backend.routes.openai_classification_routes import openai_classification_bp
except ImportError:
    openai_classification_bp = None

try:
    from backend.routes.clone_search_routes import clone_search_bp
except ImportError:
    clone_search_bp = None

try:
    from backend.routes.stage3_clone_detection_routes import api as stage3_api
    from flask_restx import Api
    STAGE3_AVAILABLE = True
except ImportError:
    STAGE3_AVAILABLE = False

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Enable CORS for all routes
    CORS(app, 
         origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Register SQL Server blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(analysis_bp, url_prefix='/api')
    
    # Register existing blueprints
    if main_bp:
        try:
            app.register_blueprint(main_bp, name='main_api')
        except AssertionError:
            app.register_blueprint(main_bp, name='main_routes')
    
    if api_bp:
        try:
            app.register_blueprint(api_bp, url_prefix='/api', name='doc_analysis_api')
        except AssertionError:
            app.register_blueprint(api_bp, url_prefix='/api', name='api_routes')
    
    if parsing_bp:
        app.register_blueprint(parsing_bp, url_prefix='/api/parsing')
    
    if crypto_validation_routes:
        app.register_blueprint(crypto_validation_routes, url_prefix='/api/crypto')
    
    if ai_clone_routes:
        app.register_blueprint(ai_clone_routes, url_prefix='/api/ai-clone')
    
    if openai_classification_bp:
        app.register_blueprint(openai_classification_bp, url_prefix='/api/openai')
    
    if clone_search_bp:
        app.register_blueprint(clone_search_bp, url_prefix='/api/clone')
    
    # Register Stage 3 API if available
    if STAGE3_AVAILABLE:
        try:
            api_v1 = Api(app, version='1.0', title='Stage 3 Clone Detection API',
                         description='Enhanced clone detection with training capabilities',
                         prefix='/api/stage3')
            api_v1.add_namespace(stage3_api, path='')
        except Exception as e:
            print(f"⚠️ Could not register Stage 3 API: {e}")
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        try:
            # Test SQL Server connectivity
            from backend.services.sqlserver_db_service import sql_server_db
            stats = sql_server_db.get_database_stats()
            
            return jsonify({
                'status': 'healthy',
                'timestamp': str(datetime.now()),
                'database': 'sql_server',
                'databases': stats
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': str(datetime.now())
            }), 500
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        """Root endpoint"""
        return jsonify({
            'service': 'Authenticator.AI Backend',
            'version': '2.0-sqlserver',
            'status': 'running',
            'database': 'SQL Server',
            'endpoints': {
                'auth': '/auth/*',
                'analysis': '/api/*',
                'health': '/health',
                'docs': '/docs'
            }
        })
    
    # Generate token endpoint for testing
    @app.route('/api/v1/generate-token', methods=['POST'])
    def generate_token():
        """Generate a test token for development"""
        try:
            data = request.get_json() or {}
            
            from backend.services.auth_service_sqlserver import auth_service
            
            # Create a test user payload
            test_user = {
                'id': data.get('user_id', 'test-user-123'),
                'email': data.get('email', 'test@example.com'),
                'username': data.get('username', 'testuser')
            }
            
            token = auth_service.generate_jwt_token(test_user)
            
            return jsonify({
                'success': True,
                'token': token,
                'user': test_user
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return app

def print_routes(app):
    """Print all registered routes"""
    print("============================================================")
    print("AUTHENTICATOR.AI UNIFIED BACKEND - REGISTERED ROUTES")
    print("============================================================")
    
    routes = []
    for rule in app.url_map.iter_rules():
        methods = ', '.join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
        if methods:
            routes.append((rule.rule, methods, rule.endpoint))
    
    # Sort by route path
    routes.sort(key=lambda x: x[0])
    
    for route, methods, endpoint in routes:
        print(f"  {route:<40} [{methods:<20}] -> {endpoint}")
    
    print("=" * 60)
    print(f"Total routes: {len(routes)}")
    print("=" * 60)

if __name__ == '__main__':
    app = create_app()
    
    print("Starting Authenticator.AI Unified Backend Server (SQL Server)")
    print_routes(app)
    
    # Test SQL Server connectivity on startup
    try:
        from backend.services.sqlserver_db_service import sql_server_db
        stats = sql_server_db.get_database_stats()
        print("✅ SQL Server connectivity test passed")
        print(f"📊 Database stats: {stats}")
    except Exception as e:
        print(f"❌ SQL Server connectivity test failed: {e}")
    
    # Run the application
    app.run(
        host=getattr(Config, 'HOST', '127.0.0.1'), 
        port=getattr(Config, 'PORT', 8001), 
        debug=getattr(Config, 'DEBUG', True)
    )
