"""
Layer 6: AI Detection using heuristic-based approach
Detects AI-generated text content in documents
"""

import os
import re
import numpy as np
from typing import Dict, Any, List
import json
from collections import Counter
import math

class AIDetectionLayer:
    """
    Layer 6: AI Detection
    Uses heuristic-based approach to identify AI-generated content
    """
    
    def __init__(self):
        self.layer_name = "AI Detection"
        self.layer_number = 6
        self.model_loaded = True  # Our heuristic model is always "loaded"
        
        # AI-generated text patterns and indicators
        self.ai_indicators = {
            'repetitive_phrases': [
                'in conclusion', 'in summary', 'to summarize',
                'it is important to note', 'it should be noted',
                'furthermore', 'moreover', 'additionally',
                'on the other hand', 'in contrast', 'however',
                'as a result', 'consequently', 'therefore'
            ],
            'generic_transitions': [
                'moving on', 'turning to', 'shifting focus',
                'next,', 'additionally,', 'furthermore,'
            ],
            'ai_hedging': [
                'it appears that', 'it seems that', 'it might be',
                'one could argue', 'it is possible that',
                'potentially', 'arguably', 'presumably'
            ],
            'formal_structure': [
                'firstly,', 'secondly,', 'thirdly,',
                'first and foremost', 'last but not least'
            ]
        }
        
    def _calculate_perplexity_proxy(self, text: str) -> float:
        """
        Calculate a proxy for perplexity using word frequency analysis
        AI text often has lower perplexity (more predictable)
        """
        words = re.findall(r'\b\w+\b', text.lower())
        if len(words) < 10:
            return 0.5
            
        word_freq = Counter(words)
        total_words = len(words)
        
        # Calculate entropy-like measure
        entropy = 0
        for count in word_freq.values():
            prob = count / total_words
            entropy -= prob * math.log2(prob)
            
        # Normalize and invert (lower entropy = higher AI probability)
        max_entropy = math.log2(min(len(word_freq), 100))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # Return AI probability (lower entropy = higher AI probability)
        return 1.0 - normalized_entropy
        
    def _detect_ai_patterns(self, text: str) -> Dict[str, float]:
        """
        Detect AI-specific patterns in text
        """
        text_lower = text.lower()
        pattern_scores = {}
        
        # Check for repetitive AI phrases
        repetitive_count = sum(1 for phrase in self.ai_indicators['repetitive_phrases'] 
                             if phrase in text_lower)
        pattern_scores['repetitive_phrases'] = min(repetitive_count / 5, 1.0)
        
        # Check for generic transitions
        transition_count = sum(1 for phrase in self.ai_indicators['generic_transitions'] 
                             if phrase in text_lower)
        pattern_scores['generic_transitions'] = min(transition_count / 3, 1.0)
        
        # Check for AI hedging language
        hedging_count = sum(1 for phrase in self.ai_indicators['ai_hedging'] 
                          if phrase in text_lower)
        pattern_scores['ai_hedging'] = min(hedging_count / 3, 1.0)
        
        # Check for overly formal structure
        formal_count = sum(1 for phrase in self.ai_indicators['formal_structure'] 
                         if phrase in text_lower)
        pattern_scores['formal_structure'] = min(formal_count / 3, 1.0)
        
        return pattern_scores
        
    def _analyze_sentence_structure(self, text: str) -> float:
        """
        Analyze sentence structure patterns typical of AI text
        """
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) < 3:
            return 0.3
            
        # Calculate sentence length variance (AI tends to be more uniform)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if not sentence_lengths:
            return 0.3
            
        avg_length = np.mean(sentence_lengths)
        variance = np.var(sentence_lengths)
        
        # Lower variance suggests more AI-like uniformity
        normalized_variance = min(variance / (avg_length ** 2), 1.0) if avg_length > 0 else 0
        
        # Return AI probability (lower variance = higher AI probability)
        return 1.0 - normalized_variance
        
    def _check_vocabulary_diversity(self, text: str) -> float:
        """
        Check vocabulary diversity (AI text often has lower diversity)
        """
        words = re.findall(r'\b\w+\b', text.lower())
        if len(words) < 10:
            return 0.3
            
        unique_words = set(words)
        diversity_ratio = len(unique_words) / len(words)
        
        # Lower diversity suggests AI generation
        # Typical human text: 0.6-0.8, AI text: 0.4-0.6
        if diversity_ratio < 0.5:
            return 0.8
        elif diversity_ratio < 0.6:
            return 0.6
        elif diversity_ratio < 0.7:
            return 0.4
        else:
            return 0.2
    
    def analyze(self, file_path: str, text_content: str) -> Dict[str, Any]:
        """
        Analyze text content for AI generation using heuristic methods
        """
        try:
            if not text_content or len(text_content.strip()) < 50:
                return {
                    "status": "completed",
                    "is_ai_generated": False,
                    "ai_probability": 0.1,
                    "confidence": 0.3,
                    "method": "heuristic_analysis",
                    "details": {
                        "reason": "Text too short for reliable analysis",
                        "text_length": len(text_content.strip())
                    },
                    "processing_time": 0.2
                }
            
            # Run multiple detection methods
            perplexity_score = self._calculate_perplexity_proxy(text_content)
            pattern_scores = self._detect_ai_patterns(text_content)
            structure_score = self._analyze_sentence_structure(text_content)
            vocabulary_score = self._check_vocabulary_diversity(text_content)
            
            # Combine scores with weights
            weights = {
                'perplexity': 0.3,
                'patterns': 0.25,
                'structure': 0.25,
                'vocabulary': 0.2
            }
            
            pattern_avg = np.mean(list(pattern_scores.values()))
            
            final_score = (
                weights['perplexity'] * perplexity_score +
                weights['patterns'] * pattern_avg +
                weights['structure'] * structure_score +
                weights['vocabulary'] * vocabulary_score
            )
            
            # Determine if AI-generated (threshold: 0.6)
            is_ai_generated = final_score > 0.6
            confidence = min(abs(final_score - 0.5) * 2, 1.0)  # Distance from uncertainty
            
            return {
                "status": "completed",
                "is_ai_generated": is_ai_generated,
                "ai_probability": final_score,
                "confidence": confidence,
                "method": "heuristic_analysis",
                "details": {
                    "perplexity_proxy": perplexity_score,
                    "pattern_scores": pattern_scores,
                    "structure_score": structure_score,
                    "vocabulary_score": vocabulary_score,
                    "combined_score": final_score,
                    "threshold": 0.6
                },
                "processing_time": 0.8
            }
            
        except Exception as e:
            print(f"❌ Error in AI detection: {e}")
            return {
                "status": "error",
                "is_ai_generated": False,
                "ai_probability": 0.5,
                "confidence": 0.0,
                "method": "fallback",
                "error": str(e),
                "processing_time": 0.1
            }
    
    def get_layer_info(self) -> Dict[str, Any]:
        """Get information about this layer"""
        return {
            "layer_number": self.layer_number,
            "layer_name": self.layer_name,
            "status": "ready",
            "model_loaded": self.model_loaded,
            "method": "heuristic_analysis",
            "capabilities": [
                "Perplexity analysis",
                "Pattern detection", 
                "Sentence structure analysis",
                "Vocabulary diversity check"
            ]
        }
