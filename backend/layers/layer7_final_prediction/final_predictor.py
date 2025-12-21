"""
Layer 7: Final Prediction Model
Combines all layer results to produce final authenticity prediction
"""

import numpy as np
from typing import Dict, Any, List
import json
from datetime import datetime

class FinalPredictionLayer:
    """
    Layer 7: Final Prediction Model
    Combines results from all previous layers to make final authenticity determination
    """
    
    def __init__(self):
        self.layer_name = "Final Prediction"
        self.layer_number = 7
        
        # Layer weights for final scoring
        self.layer_weights = {
            1: 0.15,  # MIME Detection
            2: 0.20,  # Classification
            3: 0.25,  # Clone Detection
            4: 0.20,  # Cryptographic
            5: 0.05,  # RAG (when implemented)
            6: 0.15   # AI Detection
        }
        
        # Threat level thresholds
        self.threat_thresholds = {
            'low': 0.8,
            'medium': 0.6,
            'high': 0.4
        }
    
    def analyze(self, layer_results: Dict[int, Dict[str, Any]], 
                filename: str, file_size: int) -> Dict[str, Any]:
        """
        Combine all layer results into final prediction
        
        Args:
            layer_results: Dictionary of results from each layer
            filename: Original filename
            file_size: File size in bytes
            
        Returns:
            Final authenticity analysis with recommendations
        """
        try:
            # Calculate weighted authenticity score
            authenticity_score = self._calculate_authenticity_score(layer_results)
            
            # Determine threat level
            threat_level = self._determine_threat_level(authenticity_score, layer_results)
            
            # Calculate confidence
            confidence = self._calculate_confidence(layer_results)
            
            # Generate risk factors
            risk_factors = self._identify_risk_factors(layer_results)
            
            # Create recommendations
            recommendations = self._generate_recommendations(threat_level, risk_factors, layer_results)
            
            # Compile final result
            final_result = {
                "status": "completed",
                "authenticity_score": authenticity_score,
                "threat_level": threat_level,
                "confidence": confidence,
                "risk_factors": risk_factors,
                "recommendations": recommendations,
                "layer_summary": self._create_layer_summary(layer_results),
                "metadata": {
                    "filename": filename,
                    "file_size": file_size,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "layers_analyzed": list(layer_results.keys())
                },
                "layer": self.layer_number,
                "layer_name": self.layer_name
            }
            
            return final_result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "layer": self.layer_number,
                "layer_name": self.layer_name
            }
    
    def _calculate_authenticity_score(self, layer_results: Dict[int, Dict[str, Any]]) -> float:
        """Calculate weighted authenticity score"""
        total_score = 0.0
        total_weight = 0.0
        
        for layer_num, result in layer_results.items():
            if layer_num in self.layer_weights and result.get('status') == 'completed':
                score = result.get('score', 0.5)
                weight = self.layer_weights[layer_num]
                
                # Apply layer-specific adjustments
                adjusted_score = self._adjust_layer_score(layer_num, score, result)
                
                total_score += adjusted_score * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.5  # Default score if no layers completed
        
        final_score = total_score / total_weight
        return min(max(final_score, 0.0), 1.0)  # Clamp between 0 and 1
    
    def _adjust_layer_score(self, layer_num: int, score: float, result: Dict[str, Any]) -> float:
        """Apply layer-specific score adjustments"""
        adjusted_score = score
        
        if layer_num == 3:  # Clone Detection
            # If clone detected, heavily penalize authenticity
            if result.get('is_clone', False):
                adjusted_score = min(score, 0.2)
        
        elif layer_num == 6:  # AI Detection
            # If AI-generated content detected, penalize authenticity
            if result.get('is_ai_generated', False):
                ai_prob = result.get('ai_probability', 0.5)
                adjusted_score = score * (1.0 - ai_prob * 0.8)  # Reduce by up to 80%
        
        elif layer_num == 4:  # Cryptographic
            # Reward digital signatures
            if result.get('has_signature', False):
                adjusted_score = min(score * 1.2, 1.0)  # Boost by up to 20%
        
        return adjusted_score
    
    def _determine_threat_level(self, authenticity_score: float, 
                               layer_results: Dict[int, Dict[str, Any]]) -> str:
        """Determine threat level based on score and specific indicators"""
        
        # Check for critical threats
        critical_threats = []
        
        # Clone detection
        clone_result = layer_results.get(3, {})
        if clone_result.get('is_clone', False):
            critical_threats.append("Document clone detected")
        
        # AI detection
        ai_result = layer_results.get(6, {})
        if ai_result.get('is_ai_generated', False):
            ai_prob = ai_result.get('ai_probability', 0.5)
            if ai_prob > 0.8:
                critical_threats.append("High probability AI-generated content")
        
        # Cryptographic issues
        crypto_result = layer_results.get(4, {})
        if crypto_result.get('status') == 'completed' and crypto_result.get('score', 0) < 0.3:
            critical_threats.append("Cryptographic validation failed")
        
        # Determine threat level
        if critical_threats or authenticity_score < self.threat_thresholds['high']:
            return 'high'
        elif authenticity_score < self.threat_thresholds['medium']:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_confidence(self, layer_results: Dict[int, Dict[str, Any]]) -> float:
        """Calculate overall confidence in the analysis"""
        confidences = []
        
        for result in layer_results.values():
            if result.get('status') == 'completed':
                # Use confidence if available, otherwise use score as proxy
                conf = result.get('confidence', result.get('score', 0.5))
                confidences.append(conf)
        
        if not confidences:
            return 0.5
        
        # Use average confidence but penalize if few layers completed
        avg_confidence = np.mean(confidences)
        layer_coverage = len(confidences) / len(self.layer_weights)
        
        return avg_confidence * layer_coverage
    
    def _identify_risk_factors(self, layer_results: Dict[int, Dict[str, Any]]) -> List[str]:
        """Identify specific risk factors from layer results"""
        risk_factors = []
        
        # MIME Detection risks
        mime_result = layer_results.get(1, {})
        if mime_result.get('score', 1.0) < 0.7:
            risk_factors.append("Inconsistent file type detection")
        
        # Classification risks
        class_result = layer_results.get(2, {})
        if class_result.get('score', 1.0) < 0.6:
            risk_factors.append("Uncertain content classification")
        
        # Clone Detection risks
        clone_result = layer_results.get(3, {})
        if clone_result.get('is_clone', False):
            risk_factors.append("Document appears to be a duplicate")
        elif clone_result.get('similarity_score', 0) > 0.7:
            risk_factors.append("High similarity to known documents")
        
        # Cryptographic risks
        crypto_result = layer_results.get(4, {})
        if crypto_result.get('has_signature') is False:
            risk_factors.append("No digital signature present")
        
        # AI Detection risks
        ai_result = layer_results.get(6, {})
        if ai_result.get('is_ai_generated', False):
            ai_prob = ai_result.get('ai_probability', 0.5)
            if ai_prob > 0.8:
                risk_factors.append("High probability of AI-generated content")
            elif ai_prob > 0.6:
                risk_factors.append("Possible AI-generated content detected")
        
        return risk_factors
    
    def _generate_recommendations(self, threat_level: str, risk_factors: List[str],
                                 layer_results: Dict[int, Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if threat_level == 'high':
            recommendations.append("⚠️ HIGH RISK: Manual review required before use")
            recommendations.append("Consider additional verification steps")
        elif threat_level == 'medium':
            recommendations.append("⚡ MEDIUM RISK: Additional verification recommended")
        else:
            recommendations.append("✅ LOW RISK: Document appears authentic")
        
        # Specific recommendations based on risk factors
        if "Document appears to be a duplicate" in risk_factors:
            recommendations.append("Verify if this is an authorized copy")
        
        if "AI-generated content" in str(risk_factors):
            recommendations.append("Consider human verification of content authenticity")
        
        if "No digital signature present" in risk_factors:
            recommendations.append("Consider requiring digital signatures for verification")
        
        if "Inconsistent file type" in str(risk_factors):
            recommendations.append("Verify file integrity and source")
        
        return recommendations
    
    def _create_layer_summary(self, layer_results: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary of all layer results"""
        summary = {}
        
        layer_names = {
            1: "MIME Detection",
            2: "Classification", 
            3: "Clone Detection",
            4: "Cryptographic",
            5: "RAG Analysis",
            6: "AI Detection",
            7: "Final Prediction"
        }
        
        for layer_num, result in layer_results.items():
            layer_name = layer_names.get(layer_num, f"Layer {layer_num}")
            summary[layer_name] = {
                "status": result.get('status', 'unknown'),
                "score": result.get('score', 0.0),
                "details": result.get('details', 'No details available')
            }
        
        return summary

# Convenience function
def make_final_prediction(layer_results: Dict[int, Dict[str, Any]], 
                         filename: str, file_size: int) -> Dict[str, Any]:
    """
    Convenience function for final prediction
    """
    predictor = FinalPredictionLayer()
    return predictor.analyze(layer_results, filename, file_size)
