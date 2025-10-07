from flask import Blueprint, request, jsonify, send_from_directory
from flasgger import swag_from
from werkzeug.utils import secure_filename
from ..models.auth_models import db_manager, jwt_manager
import os
import hashlib
import uuid
from datetime import datetime

documents_bp = Blueprint("documents", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_user_from_token():
    """Get current user from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    payload = jwt_manager.verify_token(token)
    if not payload:
        return None
    
    return db_manager.get_user_by_id(payload['user_id'])

@documents_bp.route("/upload", methods=["POST"])
@swag_from({
    "summary": "Upload Document",
    "description": "Upload a document for analysis",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "file",
            "in": "formData",
            "type": "file",
            "required": True,
            "description": "Document file to upload"
        }
    ],
    "responses": {
        "200": {
            "description": "Document uploaded successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "document_id": {"type": "integer"},
                    "filename": {"type": "string"}
                }
            }
        },
        "400": {"description": "Invalid file or missing file"},
        "401": {"description": "Unauthorized"}
    }
})
def upload_document():
    try:
        user = get_current_user_from_token()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Calculate file hash
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Save document to database
        document_data = {
            'filename': unique_filename,
            'original_filename': original_filename,
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'mime_type': file.content_type,
            'content_hash': file_hash
        }
        
        document_id = db_manager.save_document(user['id'], document_data)
        
        return jsonify({
            "message": "Document uploaded successfully",
            "document_id": document_id,
            "filename": original_filename
        })
        
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@documents_bp.route("/list", methods=["GET"])
@swag_from({
    "summary": "List User Documents",
    "description": "Get list of all documents uploaded by the user",
    "security": [{"Bearer": []}],
    "responses": {
        "200": {
            "description": "List of documents",
            "schema": {
                "type": "object",
                "properties": {
                    "documents": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "original_filename": {"type": "string"},
                                "file_size": {"type": "integer"},
                                "mime_type": {"type": "string"},
                                "analysis_status": {"type": "string"},
                                "uploaded_at": {"type": "string"},
                                "analyzed_at": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        "401": {"description": "Unauthorized"}
    }
})
def list_documents():
    try:
        user = get_current_user_from_token()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        
        documents = db_manager.get_user_documents(user['id'])
        
        # Remove sensitive file paths
        for doc in documents:
            doc.pop('file_path', None)
            doc.pop('content_hash', None)
        
        return jsonify({"documents": documents})
        
    except Exception as e:
        print(f"List documents error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@documents_bp.route("/<int:document_id>/download", methods=["GET"])
@swag_from({
    "summary": "Download Document",
    "description": "Download a previously uploaded document",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "document_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "Document ID"
        }
    ],
    "responses": {
        "200": {"description": "Document file"},
        "404": {"description": "Document not found"},
        "401": {"description": "Unauthorized"}
    }
})
def download_document(document_id):
    try:
        user = get_current_user_from_token()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        
        # Get document from database
        documents = db_manager.get_user_documents(user['id'])
        document = next((doc for doc in documents if doc['id'] == document_id), None)
        
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        # Check if file exists
        if not os.path.exists(document['file_path']):
            return jsonify({"error": "File not found on server"}), 404
        
        directory = os.path.dirname(document['file_path'])
        filename = os.path.basename(document['file_path'])
        
        return send_from_directory(
            directory, 
            filename, 
            as_attachment=True, 
            download_name=document['original_filename']
        )
        
    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@documents_bp.route("/<int:document_id>/analyze", methods=["POST"])
@swag_from({
    "summary": "Analyze Document",
    "description": "Start analysis process for a document",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "document_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "Document ID"
        }
    ],
    "responses": {
        "200": {"description": "Analysis started"},
        "404": {"description": "Document not found"},
        "401": {"description": "Unauthorized"}
    }
})
def analyze_document(document_id):
    try:
        user = get_current_user_from_token()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        
        # Get document from database
        documents = db_manager.get_user_documents(user['id'])
        document = next((doc for doc in documents if doc['id'] == document_id), None)
        
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        # Update document status to analyzing
        db_manager.update_document_analysis(document_id, {
            'status': 'analyzing'
        })
        
        # Here you would trigger the actual analysis pipeline
        # For now, we'll just return success
        
        return jsonify({
            "message": "Analysis started",
            "document_id": document_id,
            "status": "analyzing"
        })
        
    except Exception as e:
        print(f"Analyze error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@documents_bp.route("/<int:document_id>/status", methods=["GET"])
@swag_from({
    "summary": "Get Analysis Status",
    "description": "Get current analysis status for a document",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "document_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "Document ID"
        }
    ],
    "responses": {
        "200": {"description": "Analysis status"},
        "404": {"description": "Document not found"},
        "401": {"description": "Unauthorized"}
    }
})
def get_analysis_status(document_id):
    try:
        user = get_current_user_from_token()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        
        # Get document from database
        documents = db_manager.get_user_documents(user['id'])
        document = next((doc for doc in documents if doc['id'] == document_id), None)
        
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        return jsonify({
            "document_id": document_id,
            "status": document['analysis_status'],
            "result": document.get('analysis_result'),
            "analyzed_at": document.get('analyzed_at')
        })
        
    except Exception as e:
        print(f"Status error: {e}")
        return jsonify({"error": "Internal server error"}), 500
