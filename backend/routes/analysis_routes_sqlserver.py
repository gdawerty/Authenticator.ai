"""
Analysis Routes for Authenticator.AI - SQL Server Version
Handles document analysis and storage in SQL Server databases
"""

from flask import Blueprint, request, jsonify, g
from ..services.auth_service_sqlserver import auth_service
from ..services.document_db_service_sqlserver import document_db_service
import traceback
import os
import hashlib
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

analysis_bp = Blueprint("analysis", __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'rtf'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_hash(content):
    """Generate SHA-256 hash of file content"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

@analysis_bp.route("/analyze", methods=["POST"])
@auth_service.optional_authentication
def analyze_document():
    """Analyze uploaded document and store in SQL Server"""
    try:
        user_context = auth_service.get_current_user_context()
        user_id = user_context.get('user_id', 'anonymous')
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'File type not allowed'
            }), 400
        
        # Read file content
        content = file.read()
        
        # For now, assume text content (in production, use proper text extraction)
        if file.filename.lower().endswith('.txt'):
            text_content = content.decode('utf-8')
        else:
            # Placeholder for other file types
            text_content = f"[{file.filename}] - Content extraction not yet implemented for this file type"
        
        # Generate file hash
        file_hash = get_file_hash(text_content)
        
        # Create secure filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Store document in SQL Server
        document_id = document_db_service.store_document(
            user_id=user_id,
            filename=unique_filename,
            content=text_content,
            file_type=file.content_type or 'text/plain',
            file_size=len(content),
            original_filename=filename,
            file_hash=file_hash,
            upload_path=file_path
        )
        
        # Placeholder analysis results
        analysis_results = {
            'ai_probability': 0.25,
            'human_probability': 0.75,
            'confidence': 0.85,
            'analysis_version': '1.0',
            'detected_patterns': ['natural_language_flow', 'varied_sentence_structure'],
            'risk_factors': []
        }
        
        # Store analysis results
        analysis_id = document_db_service.store_analysis_result(
            document_id=document_id,
            analysis_type='ai_detection',
            result_data=analysis_results,
            confidence_score=analysis_results['confidence'],
            processing_time=0.5
        )
        
        # Store sample highlights
        highlights = [
            {
                'highlight_type': 'human_text',
                'start_position': 0,
                'end_position': min(100, len(text_content)),
                'highlighted_text': text_content[:100],
                'confidence_score': 0.8
            }
        ]
        
        document_db_service.store_document_highlights(document_id, highlights)
        
        return jsonify({
            'success': True,
            'message': 'Document analyzed and stored successfully',
            'document_id': document_id,
            'analysis_id': analysis_id,
            'results': analysis_results,
            'highlights': highlights
        })
        
    except Exception as e:
        print(f"❌ Document analysis error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@analysis_bp.route("/documents", methods=["GET"])
@auth_service.require_authentication
def get_user_documents():
    """Get all documents for the current user"""
    try:
        user_context = auth_service.get_current_user_context()
        user_id = user_context.get('user_id')
        
        documents = document_db_service.get_user_documents(user_id)
        
        return jsonify({
            'success': True,
            'documents': documents,
            'total': len(documents)
        })
        
    except Exception as e:
        print(f"❌ Get user documents error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@analysis_bp.route("/v1/documents", methods=["GET"])
@auth_service.require_authentication
def get_user_documents_sql():
    """Get all documents for the current user from SQL Server"""
    try:
        user_context = auth_service.get_current_user_context()
        user_id = user_context.get('user_id')
        
        documents = document_db_service.get_user_documents(user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'documents': documents,
                'total': len(documents),
                'user_id': user_id
            },
            'database': 'sql_server',
            'timestamp': str(datetime.now())
        })
        
    except Exception as e:
        print(f"❌ Get user documents SQL error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@analysis_bp.route("/v1/documents/<document_id>/details", methods=["GET"])
@auth_service.require_authentication
def get_document_details(document_id):
    """Get detailed document information including analysis results"""
    try:
        user_context = auth_service.get_current_user_context()
        user_id = user_context.get('user_id')
        
        document = document_db_service.get_document_details(int(document_id), user_id)
        
        if not document:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        return jsonify({
            'success': True,
            'document': document
        })
        
    except Exception as e:
        print(f"❌ Get document details error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@analysis_bp.route("/analysis/<analysis_id>", methods=["GET"])
@auth_service.require_authentication
def get_analysis_details(analysis_id):
    """Get analysis details by ID"""
    try:
        # This would need to be implemented in the database service
        return jsonify({
            'success': False,
            'error': 'Analysis details endpoint not yet implemented'
        }), 501
        
    except Exception as e:
        print(f"❌ Get analysis details error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@analysis_bp.route("/v1/stats/database", methods=["GET"])
def get_database_stats():
    """Get database statistics"""
    try:
        from datetime import datetime
        
        stats = document_db_service.get_database_stats()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'server_info': {
                'database_type': 'SQL Server',
                'timestamp': str(datetime.now()),
                'status': 'operational'
            }
        })
        
    except Exception as e:
        print(f"❌ Get database stats error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@analysis_bp.route("/train-clone", methods=["POST"])
@auth_service.optional_authentication
def train_clone_detection():
    """Add document to clone detection training set"""
    try:
        user_context = auth_service.get_current_user_context() or {}
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'File type not allowed'
            }), 400
        
        # Read and process file
        content = file.read()
        text_content = content.decode('utf-8') if file.filename.lower().endswith('.txt') else f"[{file.filename}] - Content extraction needed"
        
        # Store in clones_db
        from ..services.sqlserver_db_service import sql_server_db
        
        document_data = {
            'filename': secure_filename(file.filename),
            'original_filename': file.filename,
            'file_hash': get_file_hash(text_content),
            'content_text': text_content,
            'file_type': file.content_type or 'text/plain',
            'file_size': len(content),
            'metadata': {
                'uploaded_by': user_context.get('user_id'),
                'purpose': 'clone_detection_training'
            }
        }
        
        training_doc_id = sql_server_db.store_clone_training_document(document_data)
        
        return jsonify({
            'success': True,
            'message': 'Document added to training set',
            'training_doc_id': training_doc_id
        })
        
    except Exception as e:
        print(f"❌ Train clone detection error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
