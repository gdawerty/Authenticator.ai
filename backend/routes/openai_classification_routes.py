from flask import Blueprint
from flask_restful import Api
from controllers.openai_classification_controller import (
    OpenAIClassificationController,
    BatchOpenAIClassificationController,
    OpenAICategoriesController,
    OpenAIClassificationHealthController
)

# Create blueprint for OpenAI classification routes
openai_classification_bp = Blueprint('openai_classification', __name__, url_prefix='/api/openai/classification')
openai_classification_api = Api(openai_classification_bp)

# Register routes
openai_classification_api.add_resource(OpenAIClassificationController, '/classify')
openai_classification_api.add_resource(BatchOpenAIClassificationController, '/batch-classify')
openai_classification_api.add_resource(OpenAICategoriesController, '/categories')
openai_classification_api.add_resource(OpenAIClassificationHealthController, '/health')

# Optional: Add route documentation
@openai_classification_bp.route('/')
def api_info():
    """
    OpenAI Classification API Information
    
    Available endpoints:
    - POST /api/openai/classification/classify - Classify single document
    - POST /api/openai/classification/batch-classify - Classify multiple documents
    - GET /api/openai/classification/categories - Get available categories
    - GET /api/openai/classification/health - Health check
    
    For detailed API documentation, see the individual endpoint implementations.
    """
    return {
        'service': 'OpenAI Document Classification API',
        'version': '1.0.0',
        'description': 'AI-powered document classification using OpenAI GPT models',
        'endpoints': {
            'classify': {
                'method': 'POST',
                'path': '/api/openai/classification/classify',
                'description': 'Classify a single document into category and subcategory'
            },
            'batch_classify': {
                'method': 'POST',
                'path': '/api/openai/classification/batch-classify',
                'description': 'Classify multiple documents in batch'
            },
            'categories': {
                'method': 'GET',
                'path': '/api/openai/classification/categories',
                'description': 'Get all available classification categories and subcategories'
            },
            'health': {
                'method': 'GET',
                'path': '/api/openai/classification/health',
                'description': 'Health check for the classification service'
            }
        },
        'models_supported': ['gpt-4o-mini'],
        'categories_supported': [
            'Financial', 'Legal', 'Medical', 'Educational', 
            'Government', 'Business', 'Personal', 'Other'
        ]
    }
