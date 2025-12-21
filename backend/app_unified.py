"""
Unified Authenticator.AI Backend
Combines app.py and app_minimal.py with enhanced features for production deployment
"""

import os
import sys
import jwt
import ssl
from datetime import datetime, timedelta
from functools import wraps
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix SSL certificate verification for NLTK downloads
ssl._create_default_https_context = ssl._create_unverified_context

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from backend.config.config import Config

# Import all route blueprints
from backend.routes.auth_routes import auth_bp
from backend.routes.documents_routes import documents_bp
from backend.routes.analysis_routes import analysis_bp

# Import comprehensive route modules
try:
    from backend.routes.main_routes import main_bp
except ImportError:
    main_bp = None

try:
    from backend.routes.api_routes import api_bp
except ImportError:
    api_bp = None

try:
    from backend.routes.ml_classification_routes import ml_bp
except ImportError:
    ml_bp = None

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
    from backend.routes.authenticity_routes import authenticity_bp
except ImportError:
    authenticity_bp = None

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

# Import document analysis API
try:
    from backend.routes.api_document_analysis import api_bp as doc_analysis_bp
except ImportError:
    doc_analysis_bp = None

# Import explanation routes
try:
    from backend.routes.explanation_routes import explanation_bp
except ImportError:
    explanation_bp = None

# Authentication middleware
def token_required(f):
    """JWT token verification decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                pass
        
        # For development, allow anonymous access but set default user
        if not token:
            g.user_id = 'anonymous'
            g.user_email = 'anonymous@example.com'
            return f(*args, **kwargs)
        
        try:
            # Decode JWT token
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            g.user_id = data['user_id']
            g.user_email = data.get('email', 'user@example.com')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def optional_auth(f):
    """Optional authentication decorator - sets user context if token is provided"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                pass
        
        # Set default anonymous user
        g.user_id = 'anonymous'
        g.user_email = 'anonymous@example.com'
        
        if token:
            try:
                data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
                g.user_id = data['user_id']
                g.user_email = data.get('email', 'user@example.com')
            except:
                pass  # Continue with anonymous user
        
        return f(*args, **kwargs)
    
    return decorated

def create_app():
    """Create and configure the unified Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enhanced CORS configuration
    CORS(app, 
         origins=[
             "http://localhost:3000", "http://localhost:3001",
             "http://localhost:5173", "http://localhost:5174", "http://localhost:5175",
             "http://localhost:8000", "http://localhost:8080", "http://localhost:8001", "http://localhost:8002",
             "http://127.0.0.1:3000", "http://127.0.0.1:5173", "http://127.0.0.1:8000"
         ],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"])
    
    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'tmp'), exist_ok=True)
    
    # Apply authentication middleware to protected routes
    @app.before_request
    def before_request():
        # Skip auth for certain routes
        skip_auth_routes = [
            '/', '/health', '/api/v1/layer-info',
            '/auth/register', '/auth/login', '/auth/callback'
        ]
        
        if request.endpoint in skip_auth_routes or request.path in skip_auth_routes:
            return
        
        # Apply optional auth to upload and analysis routes
        if request.path.startswith('/api/') or request.path.startswith('/upload'):
            optional_auth(lambda: None)()
    
    # Register core blueprints (always available)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.register_blueprint(analysis_bp, url_prefix='/api')
    
    # Register main routes if available
    if main_bp:
        app.register_blueprint(main_bp)
    
    # Register API routes if available
    if api_bp:
        app.register_blueprint(api_bp, name='main_api')
    
    # Register document analysis API
    if doc_analysis_bp:
        app.register_blueprint(doc_analysis_bp, name='doc_analysis_api')
    
    # Register optional service blueprints
    if ml_bp:
        app.register_blueprint(ml_bp, url_prefix='/api/ml')
    
    if parsing_bp:
        app.register_blueprint(parsing_bp, url_prefix='/api/parsing')
        
    if crypto_validation_routes:
        app.register_blueprint(crypto_validation_routes, url_prefix='/api/crypto')
        
    if ai_clone_routes:
        app.register_blueprint(ai_clone_routes, url_prefix='/api/ai-clone')
    
    if openai_classification_bp:
        app.register_blueprint(openai_classification_bp, url_prefix='/api/openai')
    
    if authenticity_bp:
        app.register_blueprint(authenticity_bp, url_prefix='/api/authenticity')
    
    if clone_search_bp:
        app.register_blueprint(clone_search_bp, url_prefix='/api/clone')

    if explanation_bp:
        app.register_blueprint(explanation_bp, url_prefix='/api/explanations')

    # Register Stage 3 API with Flask-RESTX if available
    if STAGE3_AVAILABLE:
        api = Api(app, doc='/api/stage3/doc/', version='1.0', title='Stage 3 Clone Detection API')
        api.add_namespace(stage3_api, path='/api/stage3')
    
    @app.route('/')
    def index():
        """Enhanced service discovery endpoint"""
        services = [
            "JWT Authentication & Authorization",
            "OAuth Integration (Google, Microsoft, GitHub, Discord)",
            "Document Upload & Secure Management",
            "User Registration & Session Management",
            "7-Layer Document Analysis Pipeline",
            "MIME Type Detection & Validation",
            "BERT-based Classification",
            "Advanced AI Clone Detection",
            "Cryptographic Validation & Digital Signatures",
            "AI Content Detection (Fast-DetectGPT)",
            "Visual Document Highlighting with Offset Mapping",
            "Real-time Analysis API with WebSocket Support",
            "Document History & Audit Trails",
            "Similarity Indexing & Vector Search"
        ]
        
        # Add available optional services
        optional_services = []
        if ml_bp:
            optional_services.append("ML Classification API")
        if parsing_bp:
            optional_services.append("Document Parsing & OCR")
        if crypto_validation_routes:
            optional_services.append("Advanced Cryptographic Validation")
        if ai_clone_routes:
            optional_services.append("Enhanced AI Clone Detection")
        if doc_analysis_bp:
            optional_services.append("Comprehensive Document Analysis API")
        if STAGE3_AVAILABLE:
            optional_services.append("Stage 3 Clone Detection with Flask-RESTX")
            
        return {
            "message": "Authenticator.AI Unified Backend",
            "version": "2.0.0",
            "status": "production-ready",
            "core_services": services,
            "optional_services": optional_services,
            "endpoints": {
                "analysis": "/api/v1/analyze-document",
                "training": "/api/ai-clone/train",
                "auth": "/auth/*",
                "health": "/health",
                "document_highlights": "/api/v1/document-highlights/<doc_id>",
                "analysis_history": "/api/v1/analysis-history",
                "layer_info": "/api/v1/layer-info",
                "documents": "/api/documents/*",
                "user_profile": "/auth/profile",
                "crypto_validation": "/api/crypto/*",
                "stage3_docs": "/api/stage3/doc/" if STAGE3_AVAILABLE else None
            },
            "authentication": {
                "required_for": ["document_upload", "analysis_storage", "user_data"],
                "optional_for": ["public_analysis", "layer_info"],
                "methods": ["JWT", "OAuth2"]
            }
        }
    
    @app.route('/health')
    def health():
        """Enhanced health check endpoint"""
        return {
            "status": "healthy",
            "service": "authenticator-ai-unified",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "auth": True,
                "documents": True,
                "analysis": True,
                "ml_classification": ml_bp is not None,
                "parsing": parsing_bp is not None,
                "crypto_validation": crypto_validation_routes is not None,
                "ai_clone": ai_clone_routes is not None,
                "stage3_api": STAGE3_AVAILABLE,
                "doc_analysis": doc_analysis_bp is not None
            }
        }
    
    @app.route('/api/v1/generate-token', methods=['POST'])
    def generate_token():
        """Development endpoint to generate JWT tokens"""
        data = request.get_json()
        user_id = data.get('user_id', 'dev_user')
        email = data.get('email', 'dev@example.com')
        
        token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, Config.SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'token': token,
            'expires_in': 86400,
            'user_id': user_id,
            'email': email
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'message': f'The requested URL {request.url} was not found on the server.',
            'available_endpoints': [rule.rule for rule in app.url_map.iter_rules()]
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again later.',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    return app

def print_routes(app):
    """Print all registered routes for debugging"""
    print("=" * 60)
    print("AUTHENTICATOR.AI UNIFIED BACKEND - REGISTERED ROUTES")
    print("=" * 60)
    
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
    
    print("Starting Authenticator.AI Unified Backend Server")
    print_routes(app)
    
    # Run the application
    app.run(
        host=getattr(Config, 'HOST', '127.0.0.1'),
        port=getattr(Config, 'PORT', 8000),
        debug=getattr(Config, 'DEBUG', True)
    )
