from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from ..services.data_service_ml import process_upload, analyze_document
from ..services.parsing_service import ParsingService
from ..services.bert_classification_service import classify_document_bert
from ..services.vit_classification_service import classify_image, get_model_info as get_vit_model_info

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp,
         title="Authenticator.ai API",
         version="1.0",
         description="API for document authentication and analysis",
         doc="/")

# Models for request/response documentation
upload_response = api.model('UploadResponse', {
    'file_id': fields.String(description='Unique identifier for the uploaded file'),
    'filename': fields.String(description='Original filename'),
    'status': fields.String(description='Upload status'),
    'mime_type': fields.String(description='Detected MIME type of the file')
})

analysis_request = api.model('AnalysisRequest', {
    'file_id': fields.String(required=True, description='File ID from upload response'),
    'analysis_type': fields.String(required=True, description='Type of analysis to perform', 
                                 enum=['authenticity', 'content', 'metadata', 'comprehensive'],
                                 example='comprehensive')
})

authenticity_metrics = api.model('AuthenticityMetrics', {
    'content_consistency': fields.Float(description='Score for content consistency'),
    'metadata_integrity': fields.Float(description='Score for metadata integrity'),
    'format_validation': fields.Float(description='Score for format validation'),
    'style_consistency': fields.Float(description='Score for style consistency')
})

domain_classification = api.model('DomainClassification', {
    'main_category': fields.String(description='Primary document category'),
    'subcategory': fields.String(description='Document subcategory'),
    'hierarchical_label': fields.String(description='Full hierarchical label'),
    'confidence': fields.Float(description='Classification confidence score'),
    'label_id': fields.Integer(description='Numeric label identifier')
})

bert_prediction = api.model('BERTPrediction', {
    'main_category': fields.String(description='Main document category'),
    'subcategory': fields.String(description='Document subcategory'),
    'hierarchical_label': fields.String(description='Full hierarchical label'),
    'confidence': fields.Float(description='Prediction confidence score'),
    'label_id': fields.Integer(description='Label ID'),
    'top_predictions': fields.List(fields.Nested(domain_classification), description='Top 5 predictions')
})

content_analysis = api.model('ContentAnalysis', {
    'language': fields.String(description='Detected document language'),
    'complexity_score': fields.Float(description='Document complexity score'),
    'formality_score': fields.Float(description='Document formality score'),
    'tone': fields.String(description='Overall document tone')
})

ai_detection = api.model('AIDetection', {
    'ai_generated_score': fields.Float(description='Probability of AI generation'),
    'human_authored_confidence': fields.Float(description='Confidence in human authorship'),
    'detection_method': fields.String(description='Method used for detection')
})

security_analysis = api.model('SecurityAnalysis', {
    'encryption': fields.String(description='Document encryption status'),
    'digital_signatures': fields.List(fields.String, description='Digital signature validation results'),
    'timestamp_validation': fields.String(description='Timestamp validation status')
})

analysis_response = api.model('AnalysisResponse', {
    'test': fields.String(description='Test'),
    'file_id': fields.String(description='File ID that was analyzed'),
    'timestamp': fields.DateTime(description='Analysis timestamp'),
    'filename': fields.String(description='Original filename'),
    'authenticity_score': fields.Float(description='Overall authenticity score (0-1)'),
    'domain_classification': fields.Nested(domain_classification),
    'authenticity_metrics': fields.Nested(authenticity_metrics),
    'content_analysis': fields.Nested(content_analysis),
    'ai_detection': fields.Nested(ai_detection),
    'security_analysis': fields.Nested(security_analysis),
    'recommendations': fields.Raw(description='Recommendations for document handling'),
    'metadata': fields.Raw(description='Additional document metadata')
})

# Parser for file upload
upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                          type=FileStorage, required=True,
                          help='Document file to upload')

@api.route('/upload')
@api.expect(upload_parser)
class UploadResource(Resource):
    """File upload endpoint"""
    @api.doc('upload_file')
    @api.response(200, 'Success', upload_response)
    @api.response(400, 'Invalid file')
    def post(self):
        """Upload a document for analysis"""
        args = upload_parser.parse_args()
        uploaded_file = args['file']
        
        if uploaded_file:
            result = process_upload(uploaded_file)
            return result, 200
        return {'error': 'No file provided'}, 400

# Text classification request model
text_classification_request = api.model('TextClassificationRequest', {
    'text': fields.String(required=True, description='Text content to classify'),
    'return_top_predictions': fields.Boolean(default=False, description='Return top 5 predictions')
})

@api.route('/classify/text')
@api.expect(text_classification_request)
class TextClassificationResource(Resource):
    """Text classification endpoint using BERT"""
    @api.doc('classify_text')
    @api.response(200, 'Success', bert_prediction)
    @api.response(400, 'Invalid input')
    def post(self):
        """Classify document text using BERT model"""
        try:
            data = request.get_json()
            if not data or 'text' not in data:
                return {'error': 'Text content is required'}, 400
            
            text = data['text']
            return_top = data.get('return_top_predictions', False)
            
            if not text or not isinstance(text, str):
                return {'error': 'Text must be a non-empty string'}, 400
            
            # Classify using BERT service
            result = classify_document_bert(text)
            
            return {
                'status': 'success',
                'classification': result,
                'timestamp': datetime.utcnow().isoformat()
            }, 200
            
        except Exception as e:
            return {'error': f'Classification failed: {str(e)}'}, 500

@api.route('/classify/health')
class ClassificationHealthResource(Resource):
    """Health check for BERT classification service"""
    @api.doc('classification_health')
    def get(self):
        """Check BERT classification service health"""
        try:
            from ..services.bert_classification_service import get_model_info
            health = get_model_info()
            return health, 200
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}, 500

@api.route('/classify/categories')
class CategoriesInfoResource(Resource):
    """Get information about available categories"""
    @api.doc('get_categories')
    def get(self):
        """Get information about available document categories"""
        try:
            from ..services.bert_classification_service import get_model_info
            category_info = get_model_info()
            return category_info, 200
        except Exception as e:
            return {'error': f'Failed to get category info: {str(e)}'}, 500

# Image classification request model
image_classification_request = api.model('ImageClassificationRequest', {
    'file': fields.Raw(required=True, description='Image file to classify')
})

vit_prediction = api.model('ViTPrediction', {
    'success': fields.Boolean(description='Whether classification was successful'),
    'top_prediction': fields.Raw(description='Top prediction result'),
    'all_predictions': fields.List(fields.Raw, description='All predictions'),
    'model_info': fields.Raw(description='Model information'),
    'error': fields.String(description='Error message if failed')
})

@api.route('/classify/image')
@api.expect(image_classification_request)
class ImageClassificationResource(Resource):
    """Image classification endpoint using ViT"""
    @api.doc('classify_image')
    @api.response(200, 'Success', vit_prediction)
    @api.response(400, 'Invalid input')
    def post(self):
        """Classify document image using ViT model"""
        try:
            if 'file' not in request.files:
                return {'error': 'Image file is required'}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {'error': 'No file selected'}, 400
            
            # Read image bytes
            image_bytes = file.read()
            
            # Classify using ViT service
            result = classify_image(image_bytes)
            
            return {
                'status': 'success',
                'classification': result,
                'timestamp': datetime.utcnow().isoformat()
            }, 200
            
        except Exception as e:
            return {'error': f'Image classification failed: {str(e)}'}, 500

@api.route('/classify/vit/health')
class ViTHealthResource(Resource):
    """Health check for ViT classification service"""
    @api.doc('vit_health')
    def get(self):
        """Check ViT classification service health"""
        try:
            health = get_vit_model_info()
            return health, 200
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}, 500

@api.route('/analyze')
class AnalyzeResource(Resource):
    """Document analysis endpoint"""
    
    # Create a parser for analyze endpoint
    analyze_parser = api.parser()
    analyze_parser.add_argument('file', location='files',
                              type=FileStorage, required=True,
                              help='Document file to analyze')
    analyze_parser.add_argument('analysis_type',
                              type=str,
                              required=True,
                              choices=['authenticity', 'content', 'metadata', 'comprehensive'],
                              help='Type of analysis to perform',
                              location='form')
    analyze_parser.add_argument('user_id',
                              type=str,
                              required=False,
                              help='User ID for logging',
                              location='form')

    @api.doc('analyze_document')
    @api.expect(analyze_parser)
    @api.response(200, 'Success', analysis_response)
    @api.response(404, 'File not found')
    @api.response(400, 'Invalid request')
    def post(self):
        """Analyze a document directly"""
        args = self.analyze_parser.parse_args()
        file = args['file']
        analysis_type = args['analysis_type']
        
        if not file or not analysis_type:
            return {'error': 'Missing required parameters'}, 400
            
        # First upload the file
        upload_result = process_upload(file)
        if not upload_result:
            return {'error': 'File upload failed'}, 400
            
        # Then analyze it
        file_id = upload_result['file_id']
        result = analyze_document(file_id, analysis_type)
        if not result:
            return {'error': 'Analysis failed'}, 404
            
        return result, 200


# Sprint 2: OCR & Parsing Models
parsing_response = api.model('ParsingResponse', {
    'success': fields.Boolean(description='Whether parsing was successful'),
    'file_id': fields.String(description='Unique file identifier'),
    'original_filename': fields.String(description='Original filename'),
    'file_type': fields.String(description='File type (PDF, IMAGE, DOCX)'),
    'extracted_text': fields.String(description='Extracted text content'),
    'confidence_score': fields.Float(description='OCR confidence score (0-1)'),
    'metadata': fields.Raw(description='File metadata including page count, processing time'),
    'qr_codes': fields.List(fields.Raw, description='Detected QR codes'),
    'vision_tags': fields.List(fields.String, description='Vision analysis tags')
})

service_status = api.model('ServiceStatus', {
    'success': fields.Boolean(description='Service availability'),
    'status': fields.String(description='Service status'),
    'capabilities': fields.Raw(description='Available OCR and vision capabilities')
})

parsing_history = api.model('ParsingHistory', {
    'success': fields.Boolean(description='Request success'),
    'history': fields.List(fields.Raw, description='Parsing history records'),
    'total_count': fields.Integer(description='Total number of records')
})

# Initialize parsing service
parsing_service = ParsingService()

@api.route('/parse')
class Parse(Resource):
    """Sprint 2: File Parsing & OCR Endpoint"""
    
    parse_parser = api.parser()
    parse_parser.add_argument('file', location='files',
                             type=FileStorage, required=True,
                             help='File to parse (PDF, PNG, JPG, JPEG, GIF, DOCX)')
    parse_parser.add_argument('enhance_ocr', type=bool, required=False,
                             help='Whether to enhance OCR quality', default=True,
                             location='form')
    parse_parser.add_argument('detect_qr', type=bool, required=False,
                             help='Whether to detect QR codes', default=True,
                             location='form')
    parse_parser.add_argument('vision_analysis', type=bool, required=False,
                             help='Whether to perform vision analysis', default=True,
                             location='form')

    @api.doc('parse_file')
    @api.expect(parse_parser)
    @api.response(200, 'Success', parsing_response)
    @api.response(400, 'Bad request - invalid file or parameters')
    @api.response(413, 'File too large')
    @api.response(500, 'Internal server error')
    def post(self):
        """Parse uploaded file and extract content using OCR"""
        try:
            args = self.parse_parser.parse_args()
            file = args['file']
            
            if not file or file.filename == '':
                return {'success': False, 'error': 'No file provided'}, 400
            
            # Check file size (16MB limit)
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset
            
            if file_size > 16 * 1024 * 1024:  # 16MB
                return {'success': False, 'error': 'File size exceeds 16MB limit'}, 413
            
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            original_filename = secure_filename(file.filename)
            filename = f"{original_filename.rsplit('.', 1)[0]}_{timestamp}_{unique_id}.{original_filename.rsplit('.', 1)[1].lower()}"
            
            # Save file temporarily
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Get MIME type
            file_ext = original_filename.rsplit('.', 1)[1].lower()
            mime_type_map = {
                'pdf': 'application/pdf',
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'gif': 'image/gif',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
            mime_type = mime_type_map.get(file_ext, 'application/octet-stream')
            
            # Parse the file
            result = parsing_service.parse_file(file_path, original_filename, mime_type)
            
            # Add metadata
            result.update({
                'success': True,
                'file_id': f"{original_filename.rsplit('.', 1)[0]}_{timestamp}_{unique_id}",
                'original_filename': original_filename,
                'saved_filename': filename
            })
            
            return result, 200
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to parse file: {str(e)}'}, 500


@api.route('/parse/status')
class ParseStatus(Resource):
    """Check parsing service status"""
    
    @api.doc('get_parsing_status')
    @api.response(200, 'Service status', service_status)
    def get(self):
        """Get the status of the parsing service"""
        try:
            status = parsing_service.get_service_status()
            
            return {
                'success': True,
                'status': 'active',
                'capabilities': {
                    'ocr': status.get('ocr_available', True),
                    'qr_detection': status.get('qr_detection_available', False),
                    'vision_analysis': status.get('vision_analysis_available', True),
                    'supported_formats': ['PDF', 'PNG', 'JPG', 'JPEG', 'GIF', 'DOCX']
                }
            }, 200
            
        except Exception as e:
            return {'success': False, 'status': 'error', 'error': str(e)}, 500


@api.route('/parse/history')
class ParseHistory(Resource):
    """Get parsing history"""
    
    history_parser = api.parser()
    history_parser.add_argument('limit', type=int, required=False,
                               help='Maximum number of records to return', default=50,
                               location='args')

    @api.doc('get_parsing_history')
    @api.expect(history_parser)
    @api.response(200, 'Parsing history', parsing_history)
    def get(self):
        """Get the history of parsed files"""
        try:
            args = self.history_parser.parse_args()
            limit = args.get('limit', 50)
            
            # This would normally get from the parsing service
            # For now, return a simple response
            return {
                'success': True,
                'history': [],
                'total_count': 0
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve history: {str(e)}'}, 500


@api.route('/analysis/<file_id>')
class AnalysisResultResource(Resource):
    """Get analysis results by file ID"""

    @api.doc('get_analysis_result')
    @api.response(200, 'Analysis result', analysis_response)
    @api.response(404, 'Analysis not found')
    def get(self, file_id):
        """Get analysis results for a specific file ID"""
        try:
            # Get analysis result from the analysis service
            result = analyze_document(file_id, 'comprehensive')

            if not result:
                return {'error': 'Analysis not found for the given file ID'}, 404

            return result, 200

        except Exception as e:
            return {'error': f'Failed to retrieve analysis: {str(e)}'}, 500
