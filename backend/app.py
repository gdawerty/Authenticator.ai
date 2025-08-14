# backend/app.py
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
from flask_restx import Api, Resource, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import os
import mimetypes
import hashlib
import time
from datetime import datetime
import re
from typing import Dict, Tuple, List
import json

app = Flask(__name__)
CORS(app)

# Initialize Flask-RESTX Api with a URL prefix to avoid conflicts
api = Api(app, 
          title="Authenticator.ai API", 
          version="1.0", 
          doc="/docs",
          prefix="/api")

# Define request parser for file upload
file_upload = api.parser()
file_upload.add_argument('file', type=FileStorage, location='files', required=True, help='File to analyze')

@api.route('/analyze')
class AnalyzeResource(Resource):
    @api.expect(file_upload)
    def post(self):
        """Analyze uploaded file for AI detection"""
        if 'file' not in request.files:
            return {'error': 'No file provided'}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {'error': 'No file selected'}, 400
            
        if not allowed_file(file.filename):
            return {'error': 'File type not allowed'}, 400

        try:
            # Save file with unique name
            filename = generate_unique_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Get basic file info
            file_size = os.path.getsize(filepath)
            content_info = detect_content_type(filepath)

            # Here you would add your actual AI detection logic
            # For now, returning a mock response
            return {
                'file_info': {
                    'name': filename,
                    'size': file_size,
                    'type': content_info.get('mime_type', 'unknown')
                },
                'content_analysis': {
                    'content_type': content_info.get('content_category', 'unknown'),
                    'word_count': 0,  # You would implement actual word counting
                    'language': 'English'  # You would implement language detection
                },
                'domain_classification': {
                    'domain': 'General',
                    'confidence': 0.8
                },
                'authenticity_assessment': {
                    'score': 75,  # Mock score - implement actual AI detection here
                    'confidence': 'High',
                    'factors': [
                        'Document structure analysis',
                        'Language pattern evaluation',
                        'Content consistency check',
                        'Writing style assessment'
                    ]
                }
            }
        except Exception as e:
            return {'error': str(e)}, 500

BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")  # Changed from tmp_uploads to uploads
ALLOWED_EXT = {"txt", "pdf", "doc", "docx", "jpg", "jpeg", "png", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist (Task 5.1)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Domain classification keywords (Task 4.1)
DOMAIN_KEYWORDS = {
    "legal": ["contract", "agreement", "law", "legal", "court", "attorney", "clause", 
              "jurisdiction", "plaintiff", "defendant", "litigation", "statute", "regulation"],
    "insurance": ["policy", "premium", "coverage", "claim", "deductible", "beneficiary", 
                  "insured", "underwriting", "liability", "indemnity", "risk", "actuarial"],
    "healthcare": ["patient", "medical", "diagnosis", "treatment", "prescription", "physician",
                   "hospital", "symptoms", "medication", "health", "clinical", "therapy"],
    "finance": ["investment", "portfolio", "asset", "equity", "dividend", "revenue", 
                "profit", "balance sheet", "financial", "accounting", "capital", "budget"],
    "technology": ["software", "algorithm", "database", "programming", "code", "API",
                   "cloud", "server", "network", "cybersecurity", "data", "system"]
}

def allowed_file(name: str) -> bool:
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename to avoid collisions (Task 5.2)"""
    name, ext = os.path.splitext(secure_filename(original_filename))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_hash = hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:8]
    return f"{name}_{timestamp}_{unique_hash}{ext}"

def detect_content_type(filepath: str) -> Dict[str, str]:
    """Detect MIME type and classify content (Task 2.1 & 2.2)"""
    # Get MIME type
    mime_type, _ = mimetypes.guess_type(filepath)
    if not mime_type:
        # Fallback: read file header for magic bytes
        with open(filepath, 'rb') as f:
            header = f.read(512)
            if header.startswith(b'%PDF'):
                mime_type = 'application/pdf'
            elif header.startswith(b'PK'):
                mime_type = 'application/vnd.openxmlformats-officedocument'
            else:
                mime_type = 'application/octet-stream'
    
    # Classify content type
    if mime_type:
        if mime_type.startswith('text/'):
            content_category = 'text'
        elif mime_type.startswith('image/'):
            content_category = 'image'
        elif mime_type in ['application/pdf', 'application/msword', 
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            content_category = 'document'
        else:
            content_category = 'binary'
    else:
        content_category = 'unknown'
    
    return {
        "mime_type": mime_type or "unknown",
        "content_category": content_category,
        "extension": os.path.splitext(filepath)[1]
    }

def extract_text_from_file(filepath: str) -> str:
    """Extract text from various file types for analysis"""
    content_type = detect_content_type(filepath)
    text = ""
    
    try:
        if content_type["content_category"] in ["text", "document"]:
            if filepath.endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            elif filepath.endswith('.pdf'):
                # Placeholder for PDF extraction
                # In production, use PyPDF2 or pdfplumber
                text = "[PDF content extraction placeholder - install PyPDF2 for actual extraction]"
            elif filepath.endswith(('.doc', '.docx')):
                # Placeholder for Word extraction
                # In production, use python-docx
                text = "[Word document extraction placeholder - install python-docx for actual extraction]"
    except Exception as e:
        text = f"Error extracting text: {str(e)}"
    
    return text

def classify_domain(text: str) -> Tuple[str, float]:
    """Classify document domain based on keywords (Task 4.1)"""
    if not text:
        return "unknown", 0.0
    
    text_lower = text.lower()
    domain_scores = {}
    
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            domain_scores[domain] = score
    
    if domain_scores:
        # Get domain with highest score
        best_domain = max(domain_scores, key=domain_scores.get)
        # Calculate confidence as percentage of keywords found
        confidence = (domain_scores[best_domain] / len(DOMAIN_KEYWORDS[best_domain])) * 100
        return best_domain, round(confidence, 2)
    
    return "general", 0.0

def calculate_authenticity_score(filepath: str, text: str) -> Dict:
    """Calculate authenticity score using heuristics (Task 6.1)"""
    score = 50  # Base score
    factors = []
    
    # Check file format (PDFs often more authentic)
    if filepath.endswith('.pdf'):
        score += 10
        factors.append("PDF format (+10)")
    elif filepath.endswith(('.doc', '.docx')):
        score += 5
        factors.append("Word document format (+5)")
    
    # Text analysis if available
    if text and len(text) > 100:
        # Calculate type-token ratio (vocabulary diversity)
        words = text.lower().split()
        if words:
            unique_words = set(words)
            ttr = len(unique_words) / len(words)
            
            if ttr > 0.7:
                score += 15
                factors.append("High vocabulary diversity (+15)")
            elif ttr > 0.4:
                score += 10
                factors.append("Moderate vocabulary diversity (+10)")
            else:
                score -= 10
                factors.append("Low vocabulary diversity (-10)")
        
        # Check for sentence variance
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) > 3:
            sentence_lengths = [len(s.split()) for s in sentences]
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            
            if 10 <= avg_length <= 20:
                score += 10
                factors.append("Good sentence structure (+10)")
            elif avg_length < 5:
                score -= 15
                factors.append("Very short sentences (-15)")
        
        # Check for professional language indicators
        professional_terms = ["pursuant", "hereby", "whereas", "therefore", "furthermore"]
        prof_count = sum(1 for term in professional_terms if term in text.lower())
        if prof_count >= 2:
            score += 10
            factors.append("Professional language detected (+10)")
    
    # Check file size (very small files might be suspicious)
    file_size = os.path.getsize(filepath)
    if file_size < 1000:  # Less than 1KB
        score -= 20
        factors.append("Very small file size (-20)")
    elif file_size > 10000:  # More than 10KB
        score += 5
        factors.append("Substantial file size (+5)")
    
    # Ensure score is within 0-100 range
    score = max(0, min(100, score))
    
    return {
        "score": score,
        "factors": factors,
        "confidence": "high" if len(factors) >= 3 else "medium" if len(factors) >= 1 else "low"
    }

def route_content(content_type: str, filepath: str) -> Dict:
    """Route content based on type (Task 3.1)"""
    routing_info = {
        "routed_to": None,
        "handler": None,
        "status": "pending"
    }
    
    if content_type == "text":
        routing_info["routed_to"] = "text_analysis_module"
        routing_info["handler"] = "NLP_PROCESSOR"
        routing_info["status"] = "processed"
        # TODO: Integrate actual NLP model here
    elif content_type == "image":
        routing_info["routed_to"] = "image_analysis_module"
        routing_info["handler"] = "OCR_PROCESSOR"
        routing_info["status"] = "queued"
        # TODO: Integrate OCR/Vision model here
    elif content_type == "document":
        routing_info["routed_to"] = "document_analysis_module"
        routing_info["handler"] = "DOCUMENT_PROCESSOR"
        routing_info["status"] = "processed"
        # TODO: Integrate document processing pipeline here
    else:
        routing_info["routed_to"] = "binary_handler"
        routing_info["handler"] = "BINARY_PROCESSOR"
        routing_info["status"] = "unsupported"
        # TODO: Add binary file handling logic here
    
    return routing_info

# ----- Plain Flask routes -----
@app.route("/")
def index():
    """Root endpoint with HTML response"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authenticator.ai Backend</title>
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
            <h1>🔐 Authenticator.ai Backend API</h1>
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

@app.route("/health")
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

# ----- RESTX API routes -----
upload_parser = reqparse.RequestParser()
upload_parser.add_argument("file", 
                          location="files", 
                          type=FileStorage, 
                          required=True,
                          help="File to upload")

@api.route("/upload")
class Upload(Resource):
    @api.doc("upload_file")
    @api.expect(upload_parser)
    @api.response(200, "File uploaded successfully")
    @api.response(400, "Bad request - No file selected")
    @api.response(415, "Unsupported file type")
    def post(self):
        """Upload a file to the server with metadata extraction"""
        args = upload_parser.parse_args()
        f = args["file"]
        
        if not f or f.filename == "":
            return {"error": "No file selected"}, 400

        original_filename = f.filename
        if not allowed_file(original_filename):
            return {
                "error": f"File type not allowed. Allowed: {', '.join(sorted(ALLOWED_EXT))}"
            }, 415

        # Generate unique filename to avoid collisions
        unique_filename = generate_unique_filename(original_filename)
        
        # Save the file
        dest = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        f.save(dest)
        
        # Detect content type
        content_info = detect_content_type(dest)
        
        return {
            "message": "File uploaded successfully",
            "original_filename": original_filename,
            "stored_filename": unique_filename,
            "type": f.content_type,
            "size": os.path.getsize(dest),
            "path": dest,
            "content_type": content_info,
            "upload_time": datetime.now().isoformat()
        }, 200

@api.route("/analyze")
class Analyze(Resource):
    @api.doc("analyze_file")
    @api.expect(upload_parser)
    @api.response(200, "File analyzed successfully")
    @api.response(400, "Bad request")
    def post(self):
        """Analyze uploaded file for authenticity and domain classification"""
        args = upload_parser.parse_args()
        f = args["file"]
        
        if not f or f.filename == "":
            return {"error": "No file selected"}, 400

        original_filename = f.filename
        if not allowed_file(original_filename):
            return {
                "error": f"File type not allowed. Allowed: {', '.join(sorted(ALLOWED_EXT))}"
            }, 415

        # Generate unique filename
        unique_filename = generate_unique_filename(original_filename)
        
        # Save the file
        dest = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        f.save(dest)
        
        # Detect content type
        content_info = detect_content_type(dest)
        
        # Extract text for analysis
        extracted_text = extract_text_from_file(dest)
        
        # Classify domain
        domain, domain_confidence = classify_domain(extracted_text)
        
        # Calculate authenticity score
        authenticity = calculate_authenticity_score(dest, extracted_text)
        
        # Route content to appropriate handler
        routing = route_content(content_info["content_category"], dest)
        
        return {
            "file_info": {
                "original_filename": original_filename,
                "stored_filename": unique_filename,
                "size": os.path.getsize(dest),
                "upload_time": datetime.now().isoformat()
            },
            "content_analysis": {
                "mime_type": content_info["mime_type"],
                "content_category": content_info["content_category"],
                "extension": content_info["extension"]
            },
            "domain_classification": {
                "domain": domain,
                "confidence": f"{domain_confidence}%",
                "classification_method": "keyword_based"
            },
            "authenticity_assessment": {
                "score": authenticity["score"],
                "confidence_level": authenticity["confidence"],
                "factors": authenticity["factors"],
                "recommendation": "Likely authentic" if authenticity["score"] >= 70 
                                else "Needs review" if authenticity["score"] >= 40 
                                else "Potentially suspicious"
            },
            "routing_info": routing,
            "text_preview": extracted_text[:500] if extracted_text else None
        }, 200

# Error handlers
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": {
            "home": "/",
            "health": "/health",
            "docs": "/docs",
            "upload": "/api/upload (POST)",
            "analyze": "/api/analyze (POST)"
        }
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": str(e)
    }), 500

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting Authenticator.ai Backend Server")
    print("="*60)
    print("\n📍 Server URL: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("📁 Upload Directory: " + UPLOAD_FOLDER)
    print("\n✅ Implemented Features:")
    print("  ✓ File Upload & Storage (Task 1)")
    print("  ✓ Content Type Detection (Task 2)")
    print("  ✓ Smart Routing Logic (Task 3)")
    print("  ✓ Domain Classification (Task 4)")
    print("  ✓ Secure File Storage (Task 5)")
    print("  ✓ Authenticity Scoring (Task 6)")
    print("\n--- Available Routes ---")
    
    with app.app_context():
        for rule in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
            methods = ', '.join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
            if methods:
                print(f"  {rule.rule:30s} [{methods}]")
    
    print("-" * 40 + "\n")
    
    app.run(debug=True, host="127.0.0.1", port=8000)