"""
Analysis Layer Explanation Integration Service
Adds Groq-powered explanations to each layer of the analysis pipeline
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from .groq_explanation_service import get_groq_service

class LayerExplanationIntegrator:
    """Integrates Groq explanations into analysis pipeline"""
    
    def __init__(self):
        """Initialize the explanation integrator"""
        self.groq_service = get_groq_service()
    
    def add_explanations_to_result(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Add Groq-generated explanations to analysis result"""
        
        if not analysis_result.get('layerResults'):
            return analysis_result
        
        # Add explanations to each layer
        for layer in analysis_result.get('layerResults', []):
            layer_num = layer.get('layer')

            if layer_num == 1:
                layer['explanation'] = self.groq_service.generate_layer_1_explanation(layer.get('result', {}))
            elif layer_num == 2:
                layer['explanation'] = self.groq_service.generate_layer_2_explanation(layer.get('result', {}))
            elif layer_num == 3:
                layer['explanation'] = self.groq_service.generate_layer_3_explanation(layer.get('result', {}))
            elif layer_num == 4:
                layer['explanation'] = self.groq_service.generate_layer_4_explanation(layer.get('result', {}))
            elif layer_num == 5:
                layer['explanation'] = self.groq_service.generate_layer_5_explanation(layer.get('result', {}))
            elif layer_num == 6:
                layer['explanation'] = self.groq_service.generate_layer_6_explanation(layer.get('result', {}))
            elif layer_num == 7:
                layer['explanation'] = self.groq_service.generate_layer_7_explanation(layer.get('result', {}))
        
        # Add comprehensive explanation
        analysis_result['comprehensive_explanation'] = self.groq_service.generate_comprehensive_explanation(analysis_result)
        
        # Add metadata
        analysis_result['explanation_metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'explanation_model': 'mixtral-8x7b-32768',
            'explanation_provider': 'Groq Cloud',
            'explanation_enabled': True
        }
        
        return analysis_result
    
    def format_analysis_with_explanations(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format analysis result with explanations for frontend display"""
        
        formatted_result = {
            'analysis_id': analysis_result.get('analysis_id'),
            'timestamp': analysis_result.get('timestamp', datetime.now().isoformat()),
            'document_name': analysis_result.get('document_name'),
            'final_score': analysis_result.get('finalScore', 0),
            'classification': analysis_result.get('classification', 'Unknown'),
            'comprehensive_explanation': analysis_result.get('comprehensive_explanation'),
            'layers': []
        }
        
        # Format each layer with explanation
        for layer in analysis_result.get('layerResults', []):
            formatted_layer = {
                'layer_number': layer.get('layer'),
                'layer_type': layer.get('type'),
                'result': layer.get('result'),
                'explanation': layer.get('explanation', 'No explanation available'),
                'confidence': layer.get('confidence'),
                'timestamp': datetime.now().isoformat()
            }
            formatted_result['layers'].append(formatted_layer)
        
        # Add highlights
        formatted_result['highlights'] = analysis_result.get('highlights', [])
        
        # Add explanation metadata
        formatted_result['explanation_metadata'] = analysis_result.get('explanation_metadata', {})
        
        return formatted_result


# Singleton instance
_explanation_integrator = None

def get_explanation_integrator() -> LayerExplanationIntegrator:
    """Get or create explanation integrator singleton"""
    global _explanation_integrator
    if _explanation_integrator is None:
        _explanation_integrator = LayerExplanationIntegrator()
    return _explanation_integrator
