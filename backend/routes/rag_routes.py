"""
RAG (Retrieval-Augmented Generation) API Routes
Integrates RAG with existing classification and authenticity endpoints
"""

from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, fields
from werkzeug.datastructures import FileStorage
import os
import hashlib
from datetime import datetime
from typing import Dict, Any

# Import RAG services
from ..services.rag_enhanced_classification_service import rag_enhanced_classification_service
from ..services.rag_service import rag_service

# Create Blueprint
rag_bp = Blueprint('rag', __name__, url_prefix='/api/rag')
api = Api(rag_bp, doc='/docs/', title='RAG API', description='Retrieval-Augmented Generation API')

# Response models
rag_classification_response = api.model('RAGClassificationResponse', {
    'status': fields.String(description='Success or error status'),
    'analysis_id': fields.String(description='Unique analysis identifier'),
    'timestamp': fields.String(description='Analysis timestamp'),
    'classification': fields.Raw(description='RAG-enhanced classification results'),
    'rag_insights': fields.Raw(description='RAG insights and context'),
    'recommendations': fields.List(fields.String, description='Generated recommendations')
})

rag_similarity_response = api.model('RAGSimilarityResponse', {
    'status': fields.String(description='Success or error status'),
    'analysis_id': fields.String(description='Unique analysis identifier'),
    'similarity_analysis': fields.Raw(description='RAG-enhanced similarity analysis'),
    'rag_similarity_analysis': fields.Raw(description='RAG similarity insights'),
    'enhanced_similarity_score': fields.Float(description='Enhanced similarity score')
})

rag_comprehensive_response = api.model('RAGComprehensiveResponse', {
    'status': fields.String(description='Success or error status'),
    'analysis_id': fields.String(description='Unique analysis identifier'),
    'timestamp': fields.String(description='Analysis timestamp'),
    'classification': fields.Raw(description='RAG-enhanced classification'),
    'similarity_analysis': fields.Raw(description='RAG-enhanced similarity analysis'),
    'authenticity_verification': fields.Raw(description='RAG authenticity verification'),
    'rag_insights': fields.Raw(description='Comprehensive RAG insights'),
    'recommendations': fields.List(fields.String, description='Generated recommendations')
})

rag_status_response = api.model('RAGStatusResponse', {
    'rag_service': fields.Raw(description='RAG service statistics'),
    'classification_service': fields.Raw(description='Classification service status'),
    'integration_status': fields.String(description='Integration status'),
    'timestamp': fields.String(description='Status timestamp')
})

# Request parsers
rag_classify_parser = api.parser()
rag_classify_parser.add_argument('file', location='files', type=FileStorage, required=True, help='Document file to analyze')
rag_classify_parser.add_argument('document_type_hint', location='form', type=str, required=False, help='Optional document type hint')
rag_classify_parser.add_argument('extract_embeddings', location='form', type=bool, required=False, default=True, help='Whether to extract embeddings')

rag_similarity_parser = api.parser()
rag_similarity_parser.add_argument('text_content', location='form', type=str, required=True, help='Text content to analyze')
rag_similarity_parser.add_argument('file_id', location='form', type=str, required=True, help='Unique file identifier')
rag_similarity_parser.add_argument('filename', location='form', type=str, required=False, help='Document filename')
rag_similarity_parser.add_argument('document_type', location='form', type=str, required=False, help='Document type')

rag_comprehensive_parser = api.parser()
rag_comprehensive_parser.add_argument('file', location='files', type=FileStorage, required=True, help='Document file to analyze')
rag_comprehensive_parser.add_argument('file_id', location='form', type=str, required=True, help='Unique file identifier')
rag_comprehensive_parser.add_argument('filename', location='form', type=str, required=False, help='Document filename')
rag_comprehensive_parser.add_argument('document_type_hint', location='form', type=str, required=False, help='Optional document type hint')

@api.route('/classify')
class RAGClassification(Resource):
    """RAG-enhanced document classification"""
    
    @api.doc('rag_classify_document')
    @api.expect(rag_classify_parser)
    @api.response(200, 'Success', rag_classification_response)
    @api.response(400, 'Bad Request')
    @api.response(500, 'Internal Server Error')
    def post(self):
        """Classify document using RAG-enhanced classification"""
        try:
            args = rag_classify_parser.parse_args()
            file = args['file']
            document_type_hint = args.get('document_type_hint')
            extract_embeddings = args.get('extract_embeddings', True)
            
            if not file or file.filename == '':
                return {'error': 'No file provided'}, 400
            
            # Save file temporarily
            filename = file.filename
            file_id = hashlib.md5(f"{filename}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
            
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
                file.save(temp_file.name)
                temp_path = temp_file.name
            
            try:
                # Perform RAG-enhanced classification
                result = rag_enhanced_classification_service.classify_document_with_rag(
                    file_path=temp_path,
                    filename=filename,
                    document_type_hint=document_type_hint,
                    extract_embeddings=extract_embeddings
                )
                
                if result.get('error'):
                    return {'error': result['error']}, 500
                
                return {
                    'status': 'success',
                    'analysis_id': f"rag_classify_{file_id}",
                    'timestamp': datetime.now().isoformat(),
                    'classification': result,
                    'rag_insights': result.get('rag_enhancement', {}),
                    'recommendations': self._generate_classification_recommendations(result)
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            return {'error': f'RAG classification failed: {str(e)}'}, 500
    
    def _generate_classification_recommendations(self, result: Dict[str, Any]) -> list:
        """Generate recommendations based on classification results"""
        recommendations = []
        
        classification = result.get('classification_result', {})
        confidence = classification.get('confidence', 0)
        
        if confidence < 0.7:
            recommendations.append("Low classification confidence - consider manual review")
        
        rag_enhancement = result.get('rag_enhancement', {})
        if rag_enhancement.get('similar_documents_found', 0) > 0:
            recommendations.append(f"Found {rag_enhancement['similar_documents_found']} similar documents for context")
        
        return recommendations

@api.route('/similarity')
class RAGSimilarity(Resource):
    """RAG-enhanced document similarity analysis"""
    
    @api.doc('rag_analyze_similarity')
    @api.expect(rag_similarity_parser)
    @api.response(200, 'Success', rag_similarity_response)
    @api.response(400, 'Bad Request')
    @api.response(500, 'Internal Server Error')
    def post(self):
        """Analyze document similarity using RAG"""
        try:
            args = rag_similarity_parser.parse_args()
            text_content = args['text_content']
            file_id = args['file_id']
            filename = args.get('filename')
            document_type = args.get('document_type')
            
            if not text_content or not file_id:
                return {'error': 'text_content and file_id are required'}, 400
            
            # Perform RAG-enhanced similarity analysis
            result = rag_enhanced_classification_service.analyze_document_similarity_with_rag(
                text_content=text_content,
                file_id=file_id,
                filename=filename,
                document_type=document_type
            )
            
            if result.get('error'):
                return {'error': result['error']}, 500
            
            return {
                'status': 'success',
                'analysis_id': f"rag_similarity_{file_id}",
                'similarity_analysis': result,
                'rag_similarity_analysis': result.get('rag_similarity_analysis', {}),
                'enhanced_similarity_score': result.get('enhanced_similarity_score', 0.0)
            }
            
        except Exception as e:
            return {'error': f'RAG similarity analysis failed: {str(e)}'}, 500

@api.route('/comprehensive')
class RAGComprehensive(Resource):
    """Comprehensive RAG analysis combining all models"""
    
    @api.doc('rag_comprehensive_analysis')
    @api.expect(rag_comprehensive_parser)
    @api.response(200, 'Success', rag_comprehensive_response)
    @api.response(400, 'Bad Request')
    @api.response(500, 'Internal Server Error')
    def post(self):
        """Perform comprehensive RAG analysis"""
        try:
            args = rag_comprehensive_parser.parse_args()
            file = args['file']
            file_id = args['file_id']
            filename = args.get('filename')
            document_type_hint = args.get('document_type_hint')
            
            if not file or file.filename == '':
                return {'error': 'No file provided'}, 400
            
            if not file_id:
                return {'error': 'file_id is required'}, 400
            
            # Save file temporarily
            filename = filename or file.filename
            
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
                file.save(temp_file.name)
                temp_path = temp_file.name
            
            try:
                # Perform comprehensive RAG analysis
                result = rag_enhanced_classification_service.comprehensive_rag_analysis(
                    file_path=temp_path,
                    file_id=file_id,
                    filename=filename,
                    document_type_hint=document_type_hint
                )
                
                if result.get('error'):
                    return {'error': result['error']}, 500
                
                return {
                    'status': 'success',
                    'analysis_id': result.get('analysis_id', f"rag_comprehensive_{file_id}"),
                    'timestamp': result.get('timestamp', datetime.now().isoformat()),
                    'classification': result.get('classification', {}),
                    'similarity_analysis': result.get('similarity_analysis', {}),
                    'authenticity_verification': result.get('authenticity_verification', {}),
                    'rag_insights': result.get('rag_insights', {}),
                    'recommendations': result.get('recommendations', [])
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            return {'error': f'Comprehensive RAG analysis failed: {str(e)}'}, 500

@api.route('/retrieve')
class RAGRetrieve(Resource):
    """Retrieve similar documents using RAG"""
    
    @api.doc('rag_retrieve_similar')
    def post(self):
        """Retrieve similar documents"""
        try:
            data = request.get_json()
            query_text = data.get('query_text')
            document_type = data.get('document_type')
            top_k = data.get('top_k', 5)
            similarity_threshold = data.get('similarity_threshold', 0.7)
            
            if not query_text:
                return {'error': 'query_text is required'}, 400
            
            # Retrieve similar documents
            result = rag_service.retrieve_similar_documents(
                query_text=query_text,
                document_type=document_type,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            return {
                'status': 'success',
                'query_text': query_text,
                'retrieved_documents': result.retrieved_documents,
                'similarity_scores': result.similarity_scores,
                'context_text': result.context_text,
                'metadata': result.metadata
            }
            
        except Exception as e:
            return {'error': f'Document retrieval failed: {str(e)}'}, 500

@api.route('/status')
class RAGStatus(Resource):
    """Get RAG system status and statistics"""
    
    @api.doc('rag_system_status')
    @api.response(200, 'Success', rag_status_response)
    def get(self):
        """Get RAG system status"""
        try:
            status = rag_enhanced_classification_service.get_rag_system_status()
            return status
            
        except Exception as e:
            return {'error': f'Failed to get RAG status: {str(e)}'}, 500

@api.route('/knowledge-base/add')
class RAGAddToKnowledgeBase(Resource):
    """Add document to RAG knowledge base"""
    
    @api.doc('rag_add_to_knowledge_base')
    def post(self):
        """Add document to knowledge base"""
        try:
            data = request.get_json()
            document_id = data.get('document_id')
            filename = data.get('filename')
            content_text = data.get('content_text')
            document_type = data.get('document_type')
            classification_result = data.get('classification_result')
            authenticity_score = data.get('authenticity_score')
            metadata = data.get('metadata', {})
            
            if not all([document_id, filename, content_text, document_type]):
                return {'error': 'document_id, filename, content_text, and document_type are required'}, 400
            
            # Add to knowledge base
            success = rag_service.add_document_to_knowledge_base(
                document_id=document_id,
                filename=filename,
                content_text=content_text,
                document_type=document_type,
                classification_result=classification_result,
                authenticity_score=authenticity_score,
                metadata=metadata
            )
            
            if success:
                return {
                    'status': 'success',
                    'message': 'Document added to knowledge base',
                    'document_id': document_id
                }
            else:
                return {'error': 'Failed to add document to knowledge base'}, 500
                
        except Exception as e:
            return {'error': f'Failed to add to knowledge base: {str(e)}'}, 500

@api.route('/knowledge-base/stats')
class RAGKnowledgeBaseStats(Resource):
    """Get RAG knowledge base statistics"""
    
    @api.doc('rag_knowledge_base_stats')
    def get(self):
        """Get knowledge base statistics"""
        try:
            stats = rag_service.get_rag_statistics()
            return {
                'status': 'success',
                'statistics': stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Failed to get knowledge base stats: {str(e)}'}, 500
