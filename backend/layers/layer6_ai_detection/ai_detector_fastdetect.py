"""
Layer 6: AI Detection using Fast-Detect-GPT
Detects AI-generated text content in documents using the Fast-Detect-GPT method
"""

import os
import sys
import torch
import numpy as np
from typing import Dict, Any, Optional
import tempfile
import json
import time

# Add the fast-detect-gpt scripts to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
fast_detect_dir = os.path.join(current_dir, "fast-detect-gpt", "scripts")
if os.path.exists(fast_detect_dir):
    sys.path.insert(0, fast_detect_dir)

class AIDetectionLayer:
    """
    Layer 6: AI Detection
    Uses Fast-Detect-GPT to identify AI-generated content
    """
    
    def __init__(self):
        self.layer_name = "AI Detection"
        self.layer_number = 6
        self.model_loaded = False
        self.fast_detect_instance = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._setup_fast_detect()
        
    def _setup_fast_detect(self):
        """Setup Fast-Detect-GPT with optimal model configuration"""
        try:
            # Import Fast-DetectGPT modules
            from local_infer import FastDetectGPT
            import argparse
            
            # Use the recommended falcon-7b models for best performance
            # Fallback to smaller models if not available
            model_configs = [
                # Best performance: falcon models
                {
                    'sampling_model': 'tiiuae/falcon-7b',
                    'scoring_model': 'tiiuae/falcon-7b-instruct',
                    'description': 'Falcon 7B (best performance)'
                },
                # Fallback: GPT-Neo models (smaller, faster)
                {
                    'sampling_model': 'EleutherAI/gpt-neo-2.7B',
                    'scoring_model': 'EleutherAI/gpt-neo-2.7B',
                    'description': 'GPT-Neo 2.7B (fallback)'
                },
                # Lightweight fallback
                {
                    'sampling_model': 'EleutherAI/gpt-neo-1.3B',
                    'scoring_model': 'EleutherAI/gpt-neo-1.3B',
                    'description': 'GPT-Neo 1.3B (lightweight)'
                }
            ]
            
            # Try models in order of preference
            for config in model_configs:
                try:
                    args = argparse.Namespace(
                        sampling_model_name=config['sampling_model'],
                        scoring_model_name=config['scoring_model'],
                        device=self.device,
                        cache_dir=os.path.join(current_dir, 'model_cache')
                    )
                    
                    print(f"🔄 Loading Fast-DetectGPT with {config['description']}...")
                    self.fast_detect_instance = FastDetectGPT(args)
                    self.model_config = config
                    self.model_loaded = True
                    print(f"✅ Fast-DetectGPT loaded successfully with {config['description']}")
                    break
                    
                except Exception as e:
                    print(f"❌ Failed to load {config['description']}: {e}")
                    continue
            
            if not self.model_loaded:
                print("⚠️ Could not load any Fast-DetectGPT models, using fallback heuristic detection")
                
        except ImportError as e:
            print(f"❌ Fast-DetectGPT import failed: {e}")
            print("⚠️ Using fallback heuristic detection")
        except Exception as e:
            print(f"❌ Error setting up Fast-DetectGPT: {e}")
            print("⚠️ Using fallback heuristic detection")
    
    def analyze(self, file_path: str, text_content: str) -> Dict[str, Any]:
        """
        Analyze text content for AI generation using Fast-Detect-GPT
        """
        try:
            if not text_content or len(text_content.strip()) < 100:
                return {
                    "status": "completed",
                    "is_ai_generated": False,
                    "ai_probability": 0.1,
                    "confidence": 0.3,
                    "method": "insufficient_text",
                    "details": {
                        "reason": "Text too short for reliable AI detection",
                        "text_length": len(text_content.strip())
                    },
                    "processing_time": 0.1
                }
            
            start_time = time.time()
            
            # Use Fast-DetectGPT if available
            if self.model_loaded and self.fast_detect_instance:
                result = self._run_fast_detect_gpt(text_content)
                result["processing_time"] = time.time() - start_time
                return result
            
            # Fallback to heuristic analysis
            result = self._heuristic_ai_detection(text_content)
            result["processing_time"] = time.time() - start_time
            return result
            
        except Exception as e:
            print(f"❌ Error in AI detection analysis: {e}")
            return {
                "status": "error",
                "is_ai_generated": False,
                "ai_probability": 0.5,
                "confidence": 0.0,
                "method": "error_fallback",
                "error": str(e),
                "processing_time": 0.1
            }
    
    def _run_fast_detect_gpt(self, text_content: str) -> Dict[str, Any]:
        """
        Run Fast-Detect-GPT analysis on the text
        """
        try:
            # Clean and prepare text
            text = text_content.strip()
            
            # Split into smaller chunks if text is too long (model context limits)
            max_length = 1000  # Conservative limit for most models
            if len(text) > max_length:
                # Take first max_length characters for analysis
                text = text[:max_length]
            
            # Compute conditional probability curvature using Fast-DetectGPT
            discrepancy_score = self.fast_detect_instance.compute_crit(text)
            
            # Get probability using the pre-trained classifier
            mu0 = self.fast_detect_instance.classifier['mu0']
            sigma0 = self.fast_detect_instance.classifier['sigma0']
            mu1 = self.fast_detect_instance.classifier['mu1']
            sigma1 = self.fast_detect_instance.classifier['sigma1']
            
            # Compute probability that text is AI-generated
            from local_infer import compute_prob_norm
            ai_probability = compute_prob_norm(discrepancy_score, mu0, sigma0, mu1, sigma1)
            
            # Determine if AI-generated (threshold: 0.5)
            is_ai_generated = ai_probability > 0.5
            confidence = abs(ai_probability - 0.5) * 2  # Distance from uncertainty
            
            return {
                "status": "completed",
                "is_ai_generated": is_ai_generated,
                "ai_probability": float(ai_probability),
                "confidence": float(confidence),
                "method": "fast_detect_gpt",
                "details": {
                    "discrepancy_score": float(discrepancy_score),
                    "model_config": self.model_config['description'],
                    "sampling_model": self.model_config['sampling_model'],
                    "scoring_model": self.model_config['scoring_model'],
                    "classifier_params": {
                        "mu0": mu0, "sigma0": sigma0,
                        "mu1": mu1, "sigma1": sigma1
                    },
                    "text_length_analyzed": len(text)
                }
            }
            
        except Exception as e:
            print(f"❌ Fast-DetectGPT analysis error: {e}")
            # Fallback to heuristic if Fast-DetectGPT fails
            return self._heuristic_ai_detection(text_content)
    
    def _heuristic_ai_detection(self, text_content: str) -> Dict[str, Any]:
        """
        Fallback heuristic-based AI detection
        """
        try:
            # Simple heuristic analysis (improved version)
            ai_indicators = [
                'in conclusion', 'in summary', 'furthermore', 'moreover', 
                'additionally', 'it is important to note', 'on the other hand',
                'consequently', 'therefore', 'as a result', 'it should be noted'
            ]
            
            text_lower = text_content.lower()
            words = text_content.split()
            sentences = [s.strip() for s in text_content.split('.') if s.strip()]
            
            # Calculate metrics
            indicator_count = sum(1 for indicator in ai_indicators if indicator in text_lower)
            avg_sentence_length = len(words) / max(len(sentences), 1)
            vocabulary_diversity = len(set(words)) / len(words) if words else 0
            
            # Improved scoring with multiple factors
            pattern_score = min(indicator_count / max(len(sentences), 1), 1.0) * 0.4
            length_score = (1.0 if avg_sentence_length > 25 else avg_sentence_length / 25) * 0.3
            diversity_score = (1.0 - vocabulary_diversity) * 0.3
            
            ai_probability = min(pattern_score + length_score + diversity_score, 1.0)
            is_ai_generated = ai_probability > 0.6
            confidence = min(abs(ai_probability - 0.5) * 2, 0.8)  # Lower confidence for heuristic
            
            return {
                "status": "completed",
                "is_ai_generated": is_ai_generated,
                "ai_probability": ai_probability,
                "confidence": confidence,
                "method": "heuristic_fallback",
                "details": {
                    "indicator_count": indicator_count,
                    "avg_sentence_length": avg_sentence_length,
                    "vocabulary_diversity": vocabulary_diversity,
                    "pattern_score": pattern_score,
                    "length_score": length_score,
                    "diversity_score": diversity_score,
                    "note": "Fallback method - lower accuracy than Fast-DetectGPT"
                }
            }
            
        except Exception as e:
            print(f"❌ Heuristic analysis error: {e}")
            return {
                "status": "error",
                "is_ai_generated": False,
                "ai_probability": 0.5,
                "confidence": 0.0,
                "method": "heuristic_error",
                "error": str(e)
            }
    
    def get_layer_info(self) -> Dict[str, Any]:
        """Get information about this layer"""
        info = {
            "layer_number": self.layer_number,
            "layer_name": self.layer_name,
            "status": "ready" if self.model_loaded else "fallback_ready",
            "model_loaded": self.model_loaded,
            "device": self.device
        }
        
        if self.model_loaded and self.model_config:
            info.update({
                "method": "fast_detect_gpt",
                "model_config": self.model_config,
                "capabilities": [
                    "Fast-DetectGPT conditional probability curvature analysis",
                    "Multi-model scoring and sampling",
                    "High accuracy AI detection"
                ]
            })
        else:
            info.update({
                "method": "heuristic_fallback",
                "capabilities": [
                    "Pattern-based detection",
                    "Sentence structure analysis",
                    "Vocabulary diversity check"
                ]
            })
        
        return info
