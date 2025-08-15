from flask import Blueprint, jsonify, render_template_string, redirect

main_bp = Blueprint("main", __name__)

@main_bp.route("/docs")
def docs_redirect():
    """Redirect /docs to API documentation"""
    return redirect("/api/")

@main_bp.route("/", methods=["GET"])
def index():
    """Display welcome message and API information"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authenticator.ai API</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                max-width: 1200px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 { 
                color: #333; 
                border-bottom: 3px solid #667eea;
                padding-bottom: 15px;
            }
            .endpoint {
                background: #f8f9fa;
                padding: 15px;
                margin: 15px 0;
                border-radius: 8px;
                border-left: 4px solid #667eea;
                transition: transform 0.2s;
            }
            .endpoint:hover {
                transform: translateX(5px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
            }
            .method {
                display: inline-block;
                padding: 4px 12px;
                background: #667eea;
                color: white;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                margin-right: 10px;
            }
            .method.post { background: #28a745; }
            a { color: #667eea; text-decoration: none; font-weight: 500; }
            a:hover { text-decoration: underline; }
            .status { 
                display: inline-block;
                padding: 4px 8px;
                background: #28a745;
                color: white;
                border-radius: 4px;
                font-size: 11px;
                margin-left: 10px;
            }
            .feature-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .feature {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-top: 3px solid #764ba2;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Authenticator.ai API</h1>
            <p>Advanced document authentication and analysis service powered by AI</p>
            
            <h2>✨ Features Implemented:</h2>
            <div class="feature-list">
                <div class="feature">
                    📁 <strong>File Upload</strong><br>
                    Multi-format document support
                </div>
                <div class="feature">
                    🔍 <strong>Content Detection</strong><br>
                    MIME type & classification
                </div>
                <div class="feature">
                    🧠 <strong>Domain Classification</strong><br>
                    AI-powered content categorization
                </div>
                <div class="feature">
                    📊 <strong>Authenticity Scoring</strong><br>
                    Heuristic-based validation
                </div>
                <div class="feature">
                    🛣️ <strong>Smart Routing</strong><br>
                    Content-based processing paths
                </div>
                <div class="feature">
                    💾 <strong>Secure Storage</strong><br>
                    Collision-free file management
                </div>
            </div>
            
            <h2>📍 API Endpoints:</h2>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <strong><a href="/">/</a></strong> - API Home
                <span class="status">ACTIVE</span>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <strong><a href="/health">/health</a></strong> - Health Check
                <span class="status">ACTIVE</span>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <strong><a href="/docs">/docs</a></strong> - Interactive API Documentation
                <span class="status">ACTIVE</span>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/upload</strong> - Upload Document
                <span class="status">ACTIVE</span>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/analyze</strong> - Analyze Document
                <span class="status">ACTIVE</span>
            </div>
            
            <h2>🚀 Quick Start:</h2>
            <p>Test the API using these links:</p>
            <ul>
                <li><a href="/health">Check API Health Status</a></li>
                <li><a href="/docs">Access Swagger UI for Testing</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "API is running",
        "service": "Authenticator.ai Backend",
        "version": "1.0",
        "features": {
            "upload": "active",
            "content_detection": "active",
            "domain_classification": "active",
            "authenticity_scoring": "active",
            "smart_routing": "active"
        }
    })
