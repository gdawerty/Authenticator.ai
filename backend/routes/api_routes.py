from flask import Blueprint, request
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.datastructures import FileStorage
from ..services.data_service import process_upload, analyze_document

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
    'category': fields.String(description='Primary document category'),
    'subcategory': fields.String(description='Document subcategory'),
    'confidence': fields.Float(description='Classification confidence score')
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
