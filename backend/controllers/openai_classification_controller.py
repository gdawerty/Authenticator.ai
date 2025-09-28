import logging
from typing import Dict, List, Optional
from flask import request, jsonify
from flask_restful import Resource
from services.openai_classification_service import OpenAIClassificationService

class OpenAIClassificationController(Resource):
    """
    Controller for OpenAI document classification endpoints
    """
    
    def __init__(self):
        self.classification_service = OpenAIClassificationService()
        self.logger = logging.getLogger(__name__)
    
    def post(self):
        """
        Classify a single document
        
        Expected JSON payload:
        {
            "text_content": "Document text to classify",
            "confidence_threshold": 0.7  // optional, defaults to 0.7
        }
        
        Returns:
            JSON response with classification results
        """
        try:
            # Get request data
            data = request.get_json()
            
            if not data or 'text_content' not in data:
                return jsonify({
                    'error': 'Missing required field: text_content',
                    'status': 'error'
                }), 400
            
            text_content = data['text_content']
            confidence_threshold = data.get('confidence_threshold', 0.7)
            
            # Validate input
            if not isinstance(text_content, str) or len(text_content.strip()) == 0:
                return jsonify({
                    'error': 'text_content must be a non-empty string',
                    'status': 'error'
                }), 400
            
            if not isinstance(confidence_threshold, (int, float)) or not 0 <= confidence_threshold <= 1:
                return jsonify({
                    'error': 'confidence_threshold must be a number between 0 and 1',
                    'status': 'error'
                }), 400
            
            # Perform classification
            result = self.classification_service.classify_document(
                text_content, 
                confidence_threshold
            )
            
            return jsonify({
                'status': 'success',
                'data': result
            }), 200
            
        except Exception as e:
            self.logger.error(f"Error in classification endpoint: {str(e)}")
            return jsonify({
                'error': f'Internal server error: {str(e)}',
                'status': 'error'
            }), 500

class BatchOpenAIClassificationController(Resource):
    """
    Controller for batch OpenAI document classification
    """
    
    def __init__(self):
        self.classification_service = OpenAIClassificationService()
        self.logger = logging.getLogger(__name__)
    
    def post(self):
        """
        Classify multiple documents in batch
        
        Expected JSON payload:
        {
            "documents": [
                "Document 1 text",
                "Document 2 text",
                "Document 3 text"
            ],
            "confidence_threshold": 0.7  // optional, defaults to 0.7
        }
        
        Returns:
            JSON response with batch classification results
        """
        try:
            # Get request data
            data = request.get_json()
            
            if not data or 'documents' not in data:
                return jsonify({
                    'error': 'Missing required field: documents',
                    'status': 'error'
                }), 400
            
            documents = data['documents']
            confidence_threshold = data.get('confidence_threshold', 0.7)
            
            # Validate input
            if not isinstance(documents, list) or len(documents) == 0:
                return jsonify({
                    'error': 'documents must be a non-empty list',
                    'status': 'error'
                }), 400
            
            if len(documents) > 100:  # Limit batch size
                return jsonify({
                    'error': 'Batch size cannot exceed 100 documents',
                    'status': 'error'
                }), 400
            
            for i, doc in enumerate(documents):
                if not isinstance(doc, str) or len(doc.strip()) == 0:
                    return jsonify({
                        'error': f'Document {i} must be a non-empty string',
                        'status': 'error'
                    }), 400
            
            if not isinstance(confidence_threshold, (int, float)) or not 0 <= confidence_threshold <= 1:
                return jsonify({
                    'error': 'confidence_threshold must be a number between 0 and 1',
                    'status': 'error'
                }), 400
            
            # Perform batch classification
            results = self.classification_service.batch_classify_documents(
                documents, 
                confidence_threshold
            )
            
            # Get statistics
            stats = self.classification_service.get_classification_statistics(results)
            
            return jsonify({
                'status': 'success',
                'data': {
                    'classifications': results,
                    'statistics': stats
                }
            }), 200
            
        except Exception as e:
            self.logger.error(f"Error in batch classification endpoint: {str(e)}")
            return jsonify({
                'error': f'Internal server error: {str(e)}',
                'status': 'error'
            }), 500

class OpenAICategoriesController(Resource):
    """
    Controller for getting available classification categories
    """
    
    def __init__(self):
        self.classification_service = OpenAIClassificationService()
        self.logger = logging.getLogger(__name__)
    
    def get(self):
        """
        Get all available classification categories and subcategories
        
        Returns:
            JSON response with available categories
        """
        try:
            categories = self.classification_service.get_available_categories()
            
            return jsonify({
                'status': 'success',
                'data': {
                    'categories': categories,
                    'total_categories': len(categories),
                    'total_subcategories': sum(len(subcats) for subcats in categories.values())
                }
            }), 200
            
        except Exception as e:
            self.logger.error(f"Error in categories endpoint: {str(e)}")
            return jsonify({
                'error': f'Internal server error: {str(e)}',
                'status': 'error'
            }), 500

class OpenAIClassificationHealthController(Resource):
    """
    Controller for OpenAI classification service health check
    """
    
    def __init__(self):
        self.classification_service = OpenAIClassificationService()
        self.logger = logging.getLogger(__name__)
    
    def get(self):
        """
        Health check for the OpenAI classification service
        
        Returns:
            JSON response with service status
        """
        try:
            # Test with a simple classification
            test_text = "This is a test document for health check."
            result = self.classification_service.classify_document(test_text, 0.5)
            
            # Check if classification was successful
            if result.get('error', False):
                return jsonify({
                    'status': 'error',
                    'service': 'OpenAI Classification Service',
                    'message': 'Service is not responding correctly',
                    'error': result.get('reasoning', 'Unknown error')
                }), 503
            
            return jsonify({
                'status': 'healthy',
                'service': 'OpenAI Classification Service',
                'message': 'Service is working correctly',
                'test_classification': {
                    'category': result.get('category'),
                    'subcategory': result.get('subcategory'),
                    'confidence': result.get('confidence')
                }
            }), 200
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'error',
                'service': 'OpenAI Classification Service',
                'message': 'Service health check failed',
                'error': str(e)
            }), 503
