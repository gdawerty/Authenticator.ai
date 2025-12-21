"""
Explanation API Routes
Handles requests for layer-by-layer explanations using Groq Cloud
"""

from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, fields
import json
from datetime import datetime
from ..services.groq_explanation_service import get_groq_service
from ..services.layer_explanation_integrator import get_explanation_integrator

explanation_bp = Blueprint('explanations', __name__, url_prefix='/api/explanations')
api = Api(explanation_bp, doc='/docs/', title='Explanation API', description='Layer explanation endpoints')

# Models
explanation_response = api.model('ExplanationResponse', {
    'status': fields.String(description='Success or error status'),
    'layer': fields.Integer(description='Layer number'),
    'explanation': fields.String(description='Generated explanation'),
    'timestamp': fields.String(description='Generation timestamp')
})

comprehensive_response = api.model('ComprehensiveResponse', {
    'status': fields.String(description='Success or error status'),
    'comprehensive_explanation': fields.String(description='Overall analysis explanation'),
    'timestamp': fields.String(description='Generation timestamp')
})

@api.route('/layer/<int:layer_number>')
class LayerExplanation(Resource):
    """Get explanation for a specific layer"""
    
    @api.doc('get_layer_explanation')
    def post(self, layer_number):
        """Generate explanation for a specific layer"""
        try:
            data = request.get_json() or {}
            groq_service = get_groq_service()
            
            layer_result = data.get('layer_result', {})
            
            # Route to appropriate explanation generator
            if layer_number == 1:
                explanation = groq_service.generate_layer_1_explanation(layer_result)
            elif layer_number == 2:
                explanation = groq_service.generate_layer_2_explanation(layer_result)
            elif layer_number == 3:
                explanation = groq_service.generate_layer_3_explanation(layer_result)
            elif layer_number == 4:
                explanation = groq_service.generate_layer_4_explanation(layer_result)
            elif layer_number == 5:
                explanation = groq_service.generate_layer_5_explanation(layer_result)
            elif layer_number == 6:
                explanation = groq_service.generate_layer_6_explanation(layer_result)
            elif layer_number == 7:
                # Final Assessment - generate comprehensive explanation
                explanation = groq_service.generate_comprehensive_explanation(layer_result)
            else:
                return {
                    'status': 'error',
                    'message': f'Invalid layer number: {layer_number}'
                }, 400
            
            return {
                'status': 'success',
                'layer': layer_number,
                'explanation': explanation,
                'timestamp': datetime.now().isoformat()
            }, 200
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }, 500

@api.route('/comprehensive')
class ComprehensiveExplanation(Resource):
    """Get comprehensive explanation for entire analysis"""
    
    @api.doc('get_comprehensive_explanation')
    def post(self):
        """Generate comprehensive explanation for analysis"""
        try:
            data = request.get_json() or {}
            groq_service = get_groq_service()
            
            analysis_result = data.get('analysis_result', {})
            
            explanation = groq_service.generate_comprehensive_explanation(analysis_result)
            
            return {
                'status': 'success',
                'comprehensive_explanation': explanation,
                'timestamp': datetime.now().isoformat()
            }, 200
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }, 500

@api.route('/with-explanations')
class AnalysisWithExplanations(Resource):
    """Add explanations to analysis result"""
    
    @api.doc('add_explanations_to_analysis')
    def post(self):
        """Add Groq explanations to analysis result"""
        try:
            data = request.get_json() or {}
            integrator = get_explanation_integrator()
            
            analysis_result = data.get('analysis_result', {})
            
            # Add explanations
            enhanced_result = integrator.add_explanations_to_result(analysis_result)
            
            # Format for frontend
            formatted_result = integrator.format_analysis_with_explanations(enhanced_result)
            
            return {
                'status': 'success',
                'data': formatted_result,
                'timestamp': datetime.now().isoformat()
            }, 200
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }, 500

@api.route('/health')
class ExplanationHealth(Resource):
    """Health check for explanation service"""
    
    @api.doc('explanation_health')
    def get(self):
        """Check explanation service health"""
        groq_service = get_groq_service()
        return {
            'status': 'healthy' if groq_service.available else 'degraded',
            'explanation_service': 'Groq Cloud',
            'model': groq_service.model,
            'api_configured': groq_service.available,
            'timestamp': datetime.now().isoformat()
        }, 200
