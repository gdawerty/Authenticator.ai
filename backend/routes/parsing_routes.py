from flask import Blueprint, request, jsonify
from flasgger import swag_from
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from ..services.parsing_service import ParsingService

parsing_bp = Blueprint("parsing", __name__)
parsing_service = ParsingService()

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'doc'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@parsing_bp.route("/parse", methods=["POST"])
@swag_from({
    "summary": "Parse and Extract Content from Files",
    "description": "Parse uploaded files (PDF, images, DOCX) using OCR and extract structured content",
    "consumes": ["multipart/form-data"],
    "parameters": [
        {
            "name": "file",
            "in": "formData",
            "type": "file",
            "required": True,
            "description": "File to parse (PDF, PNG, JPG, JPEG, GIF, DOCX)"
        },
        {
            "name": "enhance_ocr",
            "in": "formData",
            "type": "boolean",
            "required": False,
            "default": True,
            "description": "Whether to enhance OCR quality using image preprocessing"
        },
        {
            "name": "detect_qr",
            "in": "formData",
            "type": "boolean",
            "required": False,
            "default": True,
            "description": "Whether to detect and decode QR codes in the document"
        },
        {
            "name": "vision_analysis",
            "in": "formData",
            "type": "boolean",
            "required": False,
            "default": True,
            "description": "Whether to perform vision analysis for content tags"
        }
    ],
    "responses": {
        "200": {
            "description": "File parsed successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True
                    },
                    "file_id": {
                        "type": "string",
                        "example": "abc123_20240811_160945"
                    },
                    "original_filename": {
                        "type": "string",
                        "example": "document.pdf"
                    },
                    "file_type": {
                        "type": "string",
                        "example": "PDF"
                    },
                    "extracted_text": {
                        "type": "string",
                        "example": "This is the extracted text content..."
                    },
                    "confidence_score": {
                        "type": "number",
                        "example": 0.95
                    },
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "page_count": {
                                "type": "integer",
                                "example": 3
                            },
                            "processing_time": {
                                "type": "number",
                                "example": 2.45
                            },
                            "file_size": {
                                "type": "integer",
                                "example": 2048576
                            }
                        }
                    },
                    "qr_codes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "data": {
                                    "type": "string",
                                    "example": "https://example.com"
                                },
                                "type": {
                                    "type": "string",
                                    "example": "QRCODE"
                                }
                            }
                        }
                    },
                    "vision_tags": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "example": ["document", "text", "business_card"]
                    }
                }
            }
        },
        "400": {
            "description": "Bad request - invalid file or parameters",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": False
                    },
                    "error": {
                        "type": "string",
                        "example": "No file provided or file type not supported"
                    }
                }
            }
        },
        "413": {
            "description": "File too large",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": False
                    },
                    "error": {
                        "type": "string",
                        "example": "File size exceeds maximum limit of 16MB"
                    }
                }
            }
        },
        "500": {
            "description": "Internal server error",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": False
                    },
                    "error": {
                        "type": "string",
                        "example": "Failed to parse file: OCR processing error"
                    }
                }
            }
        }
    }
})
def parse_file():
    """Parse uploaded file and extract content using OCR"""
    try:
        # Check if file is provided
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': f'File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB'
            }), 413
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'File type not supported. Allowed types: PDF, PNG, JPG, JPEG, GIF, DOCX'
            }), 400
        
        # Get optional parameters
        enhance_ocr = request.form.get('enhance_ocr', 'true').lower() == 'true'
        detect_qr = request.form.get('detect_qr', 'true').lower() == 'true'
        vision_analysis = request.form.get('vision_analysis', 'true').lower() == 'true'
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        original_filename = secure_filename(file.filename)
        filename = f"{original_filename.rsplit('.', 1)[0]}_{timestamp}_{unique_id}.{original_filename.rsplit('.', 1)[1].lower()}"
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Detect MIME type
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        mime_type_map = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        mime_type = mime_type_map.get(file_extension, 'application/octet-stream')
        
        # Parse the file
        result = parsing_service.parse_file(file_path, original_filename, mime_type)
        
        # Add success flag and additional metadata to result
        result.update({
            'success': True,
            'file_id': f"{original_filename.rsplit('.', 1)[0]}_{timestamp}_{unique_id}",
            'original_filename': original_filename,
            'saved_filename': filename,
            'file_path': file_path
        })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to parse file: {str(e)}'
        }), 500

@parsing_bp.route("/parse/status", methods=["GET"])
@swag_from({
    "summary": "Get Parsing Service Status",
    "description": "Check if the parsing service is available and running",
    "responses": {
        "200": {
            "description": "Service status",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True
                    },
                    "status": {
                        "type": "string",
                        "example": "active"
                    },
                    "capabilities": {
                        "type": "object",
                        "properties": {
                            "ocr": {
                                "type": "boolean",
                                "example": True
                            },
                            "qr_detection": {
                                "type": "boolean",
                                "example": True
                            },
                            "vision_analysis": {
                                "type": "boolean",
                                "example": True
                            },
                            "supported_formats": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "example": ["PDF", "PNG", "JPG", "JPEG", "GIF", "DOCX"]
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_parsing_status():
    """Get the status of the parsing service"""
    try:
        # Test if parsing service is working
        status = parsing_service.get_service_status()
        
        return jsonify({
            'success': True,
            'status': 'active',
            'capabilities': {
                'ocr': status.get('ocr_available', True),
                'qr_detection': status.get('qr_detection_available', True),
                'vision_analysis': status.get('vision_analysis_available', True),
                'supported_formats': ['PDF', 'PNG', 'JPG', 'JPEG', 'GIF', 'DOCX']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'error': f'Service unavailable: {str(e)}'
        }), 500

@parsing_bp.route("/parse/history", methods=["GET"])
@swag_from({
    "summary": "Get Parsing History",
    "description": "Get the history of parsed files from JSONL log",
    "parameters": [
        {
            "name": "limit",
            "in": "query",
            "type": "integer",
            "required": False,
            "default": 50,
            "description": "Maximum number of records to return"
        }
    ],
    "responses": {
        "200": {
            "description": "Parsing history",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True
                    },
                    "history": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "timestamp": {
                                    "type": "string",
                                    "example": "2024-08-11T16:09:45Z"
                                },
                                "file_id": {
                                    "type": "string",
                                    "example": "document_20240811_160945_abc123"
                                },
                                "original_filename": {
                                    "type": "string",
                                    "example": "document.pdf"
                                },
                                "file_type": {
                                    "type": "string",
                                    "example": "PDF"
                                },
                                "confidence_score": {
                                    "type": "number",
                                    "example": 0.95
                                },
                                "success": {
                                    "type": "boolean",
                                    "example": True
                                }
                            }
                        }
                    },
                    "total_count": {
                        "type": "integer",
                        "example": 150
                    }
                }
            }
        }
    }
})
def get_parsing_history():
    """Get the history of parsed files"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = parsing_service.get_parsing_history(limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'total_count': len(history)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve history: {str(e)}'
        }), 500
