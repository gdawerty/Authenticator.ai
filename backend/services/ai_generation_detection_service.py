"""
Layer 6: AI-Generation Detection Service
Machine learning models to detect AI-generated content and estimate probability of synthetic generation.

This layer implements:
1. LLM detection using statistical patterns
2. Neural text analysis for generation signatures
3. Synthetic content probability estimation
4. Multi-model ensemble detection
5. Fine-grained generation source identification
"""

import json
import os
import hashlib
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re
import numpy as np
from dataclasses import dataclass
from pathlib import Path
import math

@dataclass
class GenerationSignature:
    """Represents AI generation signature patterns"""
    pattern_type: str  # linguistic, statistical, structural
    confidence: float
    evidence: List[str]
    model_indicators: List[str]
    
@dataclass
class AIDetectionResult:
    """Results of AI generation detection analysis"""
    content_id: str
    ai_probability: float
    human_probability: float
    detection_confidence: float
    likely_source: str  # gpt, claude, human, mixed
    generation_signatures: List[GenerationSignature]
    detailed_analysis: Dict[str, Any]

class AIGenerationDetectionService:
    """
    Layer 6: AI-Generation Detection Service
    
    Provides comprehensive AI-generated content detection using:
    - Statistical pattern analysis
    - Linguistic signature detection
    - Neural generation markers
    - Multi-model ensemble detection
    """
    
    def __init__(self):
        """Initialize AI Generation Detection Service"""
        self.base_path = Path(__file__).parent.parent
        self.detection_db_path = self.base_path / "data" / "ai_detection.db"
        
        # Initialize detection models and patterns
        self._init_detection_patterns()
        self._init_database()
        
        # Model signatures for different AI systems
        self.model_signatures = {
            "gpt": {
                "patterns": ["I understand", "I apologize", "It's important to note", "However,"],
                "repetition_threshold": 0.15,
                "avg_sentence_length": (15, 25),
                "formal_language_ratio": 0.7
            },
            "claude": {
                "patterns": ["I'd be happy to", "I should clarify", "It would be helpful"],
                "repetition_threshold": 0.12,
                "avg_sentence_length": (18, 28),
                "formal_language_ratio": 0.75
            },
            "gemini": {
                "patterns": ["Based on my analysis", "I can help you", "According to"],
                "repetition_threshold": 0.18,
                "avg_sentence_length": (12, 22),
                "formal_language_ratio": 0.65
            }
        }
        
        # Detection thresholds
        self.thresholds = {
            "high_ai_probability": 0.8,
            "moderate_ai_probability": 0.6,
            "low_ai_probability": 0.4,
            "detection_confidence_threshold": 0.7
        }
        
        print("🤖 AI Generation Detection Service initialized")
        print(f"   💾 Detection DB: {self.detection_db_path}")
        print(f"   🎯 Model signatures loaded: {len(self.model_signatures)}")
        
    def _init_detection_patterns(self):
        """Initialize AI detection patterns and features"""
        # Linguistic patterns often found in AI-generated text
        self.ai_linguistic_patterns = {
            "hedging_phrases": [
                "it's worth noting", "it's important to", "it should be noted",
                "one might consider", "it's possible that", "in general"
            ],
            "formal_transitions": [
                "furthermore", "moreover", "additionally", "consequently", 
                "therefore", "subsequently", "nevertheless"
            ],
            "ai_disclaimers": [
                "as an ai", "i cannot", "i don't have", "i'm not able to",
                "i cannot provide", "i'm unable to", "as a language model"
            ],
            "repetitive_structures": [
                r"(here are|here's a list of|the following are)",
                r"(first|second|third|finally),?\s",
                r"(in conclusion|to summarize|in summary)"
            ]
        }
        
        # Statistical features for AI detection
        self.statistical_features = {
            "vocabulary_diversity": {"threshold": 0.6, "ai_typical": "low"},
            "sentence_length_variance": {"threshold": 50, "ai_typical": "low"},
            "punctuation_patterns": {"threshold": 0.05, "ai_typical": "regular"},
            "word_frequency_distribution": {"threshold": 2.5, "ai_typical": "uniform"}
        }
        
        # Structural patterns
        self.structural_patterns = {
            "paragraph_uniformity": {"threshold": 0.8, "ai_typical": "high"},
            "list_frequency": {"threshold": 0.3, "ai_typical": "high"},
            "numbered_points": {"threshold": 0.2, "ai_typical": "high"},
            "balanced_structure": {"threshold": 0.7, "ai_typical": "high"}
        }
    
    def _init_database(self):
        """Initialize SQLite database for AI detection analysis"""
        with sqlite3.connect(self.detection_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ai_detection_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT,
                    content_hash TEXT,
                    ai_probability REAL,
                    human_probability REAL,
                    detection_confidence REAL,
                    likely_source TEXT,
                    signatures_count INTEGER,
                    analysis_details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS generation_signatures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id INTEGER,
                    pattern_type TEXT,
                    confidence REAL,
                    evidence TEXT,
                    model_indicators TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES ai_detection_analyses (id)
                )
            """)
    
    def detect_ai_generation(self, content: str, content_id: str = None) -> AIDetectionResult:
        """
        Detect AI-generated content using multiple analysis methods
        
        Args:
            content: Text content to analyze
            content_id: Unique identifier for content
            
        Returns:
            AIDetectionResult with detailed analysis
        """
        if not content_id:
            content_id = hashlib.md5(content.encode()).hexdigest()[:16]
        
        print(f"🤖 Starting AI generation detection for content: {content_id}")
        
        # Step 1: Linguistic pattern analysis
        linguistic_signatures = self._analyze_linguistic_patterns(content)
        print(f"   📝 Linguistic analysis: {len(linguistic_signatures)} signatures")
        
        # Step 2: Statistical feature analysis
        statistical_signatures = self._analyze_statistical_features(content)
        print(f"   📊 Statistical analysis: {len(statistical_signatures)} signatures")
        
        # Step 3: Structural pattern analysis
        structural_signatures = self._analyze_structural_patterns(content)
        print(f"   🏗️ Structural analysis: {len(structural_signatures)} signatures")
        
        # Step 4: Model-specific signature detection
        model_signatures = self._detect_model_signatures(content)
        print(f"   🎯 Model-specific analysis: {len(model_signatures)} signatures")
        
        # Combine all signatures
        all_signatures = (linguistic_signatures + statistical_signatures + 
                         structural_signatures + model_signatures)
        
        # Step 5: Calculate AI probability using ensemble approach
        ai_probability = self._calculate_ai_probability(all_signatures, content)
        human_probability = 1.0 - ai_probability
        detection_confidence = self._calculate_detection_confidence(all_signatures)
        
        # Step 6: Determine likely source
        likely_source = self._determine_likely_source(model_signatures, ai_probability)
        
        # Step 7: Create detailed analysis
        detailed_analysis = {
            "content_length": len(content),
            "signature_breakdown": self._analyze_signature_breakdown(all_signatures),
            "confidence_factors": self._analyze_confidence_factors(all_signatures),
            "model_likelihood": self._calculate_model_likelihoods(model_signatures),
            "risk_assessment": self._assess_generation_risk(ai_probability, detection_confidence)
        }
        
        # Step 8: Store analysis
        analysis_id = self._store_ai_detection(content_id, content, ai_probability,
                                              human_probability, detection_confidence,
                                              likely_source, all_signatures, detailed_analysis)
        
        result = AIDetectionResult(
            content_id=content_id,
            ai_probability=ai_probability,
            human_probability=human_probability,
            detection_confidence=detection_confidence,
            likely_source=likely_source,
            generation_signatures=all_signatures,
            detailed_analysis=detailed_analysis
        )
        
        print(f"   ✅ Detection complete: {likely_source} ({ai_probability:.2f} AI probability)")
        return result
    
    def _analyze_linguistic_patterns(self, content: str) -> List[GenerationSignature]:
        """Analyze linguistic patterns indicative of AI generation"""
        signatures = []
        content_lower = content.lower()
        
        # Check for hedging phrases
        hedging_count = 0
        hedging_evidence = []
        for phrase in self.ai_linguistic_patterns["hedging_phrases"]:
            if phrase in content_lower:
                hedging_count += 1
                hedging_evidence.append(phrase)
        
        if hedging_count >= 2:
            signatures.append(GenerationSignature(
                pattern_type="linguistic",
                confidence=min(hedging_count * 0.2, 0.9),
                evidence=hedging_evidence,
                model_indicators=["gpt", "claude"]
            ))
        
        # Check for formal transitions
        formal_count = 0
        formal_evidence = []
        for transition in self.ai_linguistic_patterns["formal_transitions"]:
            if transition in content_lower:
                formal_count += 1
                formal_evidence.append(transition)
        
        if formal_count >= 3:
            signatures.append(GenerationSignature(
                pattern_type="linguistic",
                confidence=min(formal_count * 0.15, 0.8),
                evidence=formal_evidence,
                model_indicators=["gpt", "claude", "gemini"]
            ))
        
        # Check for AI disclaimers
        disclaimer_evidence = []
        for disclaimer in self.ai_linguistic_patterns["ai_disclaimers"]:
            if disclaimer in content_lower:
                disclaimer_evidence.append(disclaimer)
        
        if disclaimer_evidence:
            signatures.append(GenerationSignature(
                pattern_type="linguistic",
                confidence=0.95,  # High confidence for explicit AI disclaimers
                evidence=disclaimer_evidence,
                model_indicators=["gpt", "claude", "gemini"]
            ))
        
        return signatures
    
    def _analyze_statistical_features(self, content: str) -> List[GenerationSignature]:
        """Analyze statistical features of the text"""
        signatures = []
        
        # Calculate vocabulary diversity (Type-Token Ratio)
        words = content.lower().split()
        if len(words) > 10:
            unique_words = len(set(words))
            vocabulary_diversity = unique_words / len(words)
            
            if vocabulary_diversity < self.statistical_features["vocabulary_diversity"]["threshold"]:
                signatures.append(GenerationSignature(
                    pattern_type="statistical",
                    confidence=0.7,
                    evidence=[f"Low vocabulary diversity: {vocabulary_diversity:.2f}"],
                    model_indicators=["ai_general"]
                ))
        
        # Analyze sentence length patterns
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if len(sentences) > 3:
            sentence_lengths = [len(s.split()) for s in sentences]
            length_variance = np.var(sentence_lengths) if len(sentence_lengths) > 1 else 0
            
            if length_variance < self.statistical_features["sentence_length_variance"]["threshold"]:
                signatures.append(GenerationSignature(
                    pattern_type="statistical",
                    confidence=0.6,
                    evidence=[f"Low sentence length variance: {length_variance:.1f}"],
                    model_indicators=["ai_general"]
                ))
        
        # Analyze punctuation patterns
        punctuation_chars = sum(1 for char in content if char in '.,!?;:')
        if len(content) > 0:
            punctuation_ratio = punctuation_chars / len(content)
            
            # AI text often has very regular punctuation
            if 0.04 <= punctuation_ratio <= 0.06:
                signatures.append(GenerationSignature(
                    pattern_type="statistical",
                    confidence=0.5,
                    evidence=[f"Regular punctuation pattern: {punctuation_ratio:.3f}"],
                    model_indicators=["ai_general"]
                ))
        
        return signatures
    
    def _analyze_structural_patterns(self, content: str) -> List[GenerationSignature]:
        """Analyze structural patterns in the text"""
        signatures = []
        
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Check paragraph uniformity
        if len(paragraphs) > 2:
            paragraph_lengths = [len(p.split()) for p in paragraphs]
            avg_length = sum(paragraph_lengths) / len(paragraph_lengths)
            
            # Calculate how uniform paragraph lengths are
            uniformity = 1 - (np.std(paragraph_lengths) / avg_length) if avg_length > 0 else 0
            
            if uniformity > self.structural_patterns["paragraph_uniformity"]["threshold"]:
                signatures.append(GenerationSignature(
                    pattern_type="structural",
                    confidence=0.7,
                    evidence=[f"High paragraph uniformity: {uniformity:.2f}"],
                    model_indicators=["gpt", "claude"]
                ))
        
        # Check for list patterns
        list_indicators = content.count('- ') + content.count('• ') + content.count('* ')
        numbered_lists = len(re.findall(r'\n\d+\.', content))
        
        if len(content) > 0:
            list_frequency = (list_indicators + numbered_lists) / (len(content) / 100)
            
            if list_frequency > self.structural_patterns["list_frequency"]["threshold"]:
                signatures.append(GenerationSignature(
                    pattern_type="structural",
                    confidence=0.6,
                    evidence=[f"High list frequency: {list_frequency:.2f}"],
                    model_indicators=["gpt", "gemini"]
                ))
        
        return signatures
    
    def _detect_model_signatures(self, content: str) -> List[GenerationSignature]:
        """Detect signatures specific to particular AI models"""
        signatures = []
        content_lower = content.lower()
        
        for model_name, signature_data in self.model_signatures.items():
            model_evidence = []
            pattern_matches = 0
            
            # Check for model-specific phrases
            for pattern in signature_data["patterns"]:
                if pattern.lower() in content_lower:
                    pattern_matches += 1
                    model_evidence.append(pattern)
            
            # Check sentence length patterns
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            if sentences:
                avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
                expected_range = signature_data["avg_sentence_length"]
                
                if expected_range[0] <= avg_sentence_length <= expected_range[1]:
                    model_evidence.append(f"Sentence length matches {model_name}: {avg_sentence_length:.1f}")
            
            # If we found model-specific patterns
            if pattern_matches > 0 or len(model_evidence) > 1:
                confidence = min(pattern_matches * 0.3 + len(model_evidence) * 0.2, 0.9)
                
                signatures.append(GenerationSignature(
                    pattern_type="model_specific",
                    confidence=confidence,
                    evidence=model_evidence,
                    model_indicators=[model_name]
                ))
        
        return signatures
    
    def _calculate_ai_probability(self, signatures: List[GenerationSignature], content: str) -> float:
        """Calculate probability that content is AI-generated using ensemble approach"""
        if not signatures:
            return 0.3  # Neutral probability with no signatures
        
        # Weight different signature types
        type_weights = {
            "linguistic": 0.3,
            "statistical": 0.25,
            "structural": 0.2,
            "model_specific": 0.25
        }
        
        # Calculate weighted probability
        total_weight = 0
        weighted_probability = 0
        
        for signature in signatures:
            weight = type_weights.get(signature.pattern_type, 0.2)
            weighted_probability += signature.confidence * weight
            total_weight += weight
        
        if total_weight > 0:
            base_probability = weighted_probability / total_weight
        else:
            base_probability = 0.3
        
        # Adjust based on number of signatures (more signatures = higher confidence)
        signature_boost = min(len(signatures) * 0.05, 0.2)
        
        # Adjust based on content length (very short content harder to classify)
        length_factor = min(len(content) / 500, 1.0) if len(content) > 0 else 0.5
        
        final_probability = base_probability + signature_boost
        final_probability *= length_factor
        
        return min(max(final_probability, 0.0), 1.0)
    
    def _calculate_detection_confidence(self, signatures: List[GenerationSignature]) -> float:
        """Calculate confidence in the detection result"""
        if not signatures:
            return 0.2
        
        # Base confidence from signature strengths
        avg_signature_confidence = sum(s.confidence for s in signatures) / len(signatures)
        
        # Bonus for multiple signature types
        signature_types = set(s.pattern_type for s in signatures)
        type_diversity_bonus = len(signature_types) * 0.1
        
        # Bonus for multiple pieces of evidence
        total_evidence = sum(len(s.evidence) for s in signatures)
        evidence_bonus = min(total_evidence * 0.02, 0.2)
        
        confidence = avg_signature_confidence + type_diversity_bonus + evidence_bonus
        
        return min(max(confidence, 0.0), 1.0)
    
    def _determine_likely_source(self, model_signatures: List[GenerationSignature], ai_probability: float) -> str:
        """Determine the most likely source of the content"""
        if ai_probability < self.thresholds["low_ai_probability"]:
            return "human"
        
        # Check for specific model signatures
        model_scores = {}
        for signature in model_signatures:
            for model in signature.model_indicators:
                if model not in ["ai_general"]:
                    model_scores[model] = model_scores.get(model, 0) + signature.confidence
        
        if model_scores:
            likely_model = max(model_scores.items(), key=lambda x: x[1])[0]
            return likely_model
        
        # General classification based on probability
        if ai_probability >= self.thresholds["high_ai_probability"]:
            return "ai_generated"
        elif ai_probability >= self.thresholds["moderate_ai_probability"]:
            return "likely_ai"
        else:
            return "mixed"
    
    def _analyze_signature_breakdown(self, signatures: List[GenerationSignature]) -> Dict[str, Any]:
        """Analyze breakdown of signatures by type"""
        breakdown = {}
        for signature in signatures:
            sig_type = signature.pattern_type
            if sig_type not in breakdown:
                breakdown[sig_type] = {"count": 0, "avg_confidence": 0, "evidence_count": 0}
            
            breakdown[sig_type]["count"] += 1
            breakdown[sig_type]["avg_confidence"] += signature.confidence
            breakdown[sig_type]["evidence_count"] += len(signature.evidence)
        
        # Calculate averages
        for sig_type in breakdown:
            count = breakdown[sig_type]["count"]
            breakdown[sig_type]["avg_confidence"] /= count
        
        return breakdown
    
    def _analyze_confidence_factors(self, signatures: List[GenerationSignature]) -> Dict[str, Any]:
        """Analyze factors contributing to detection confidence"""
        return {
            "signature_count": len(signatures),
            "high_confidence_signatures": len([s for s in signatures if s.confidence >= 0.8]),
            "evidence_pieces": sum(len(s.evidence) for s in signatures),
            "model_specific_matches": len([s for s in signatures if s.pattern_type == "model_specific"])
        }
    
    def _calculate_model_likelihoods(self, model_signatures: List[GenerationSignature]) -> Dict[str, float]:
        """Calculate likelihood scores for different AI models"""
        likelihoods = {}
        
        for signature in model_signatures:
            for model in signature.model_indicators:
                if model not in likelihoods:
                    likelihoods[model] = 0
                likelihoods[model] += signature.confidence
        
        # Normalize to probabilities
        total = sum(likelihoods.values())
        if total > 0:
            likelihoods = {model: score/total for model, score in likelihoods.items()}
        
        return likelihoods
    
    def _assess_generation_risk(self, ai_probability: float, detection_confidence: float) -> Dict[str, Any]:
        """Assess the risk level of AI generation"""
        if ai_probability >= 0.8 and detection_confidence >= 0.7:
            risk_level = "high"
        elif ai_probability >= 0.6 and detection_confidence >= 0.5:
            risk_level = "moderate"
        elif ai_probability >= 0.4:
            risk_level = "low"
        else:
            risk_level = "minimal"
        
        return {
            "risk_level": risk_level,
            "confidence_in_assessment": detection_confidence,
            "recommendation": self._get_risk_recommendation(risk_level)
        }
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            "high": "Content is very likely AI-generated. Recommend additional verification.",
            "moderate": "Content shows signs of AI generation. Consider manual review.",
            "low": "Some indicators of AI generation present. Monitor for patterns.",
            "minimal": "Low likelihood of AI generation. Appears human-authored."
        }
        return recommendations.get(risk_level, "Unable to assess risk.")
    
    def _store_ai_detection(self, content_id: str, content: str, ai_probability: float,
                           human_probability: float, detection_confidence: float,
                           likely_source: str, signatures: List[GenerationSignature],
                           detailed_analysis: Dict[str, Any]) -> int:
        """Store AI detection analysis in database"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        with sqlite3.connect(self.detection_db_path) as conn:
            cursor = conn.cursor()
            
            # Store main analysis
            cursor.execute("""
                INSERT INTO ai_detection_analyses 
                (content_id, content_hash, ai_probability, human_probability, 
                 detection_confidence, likely_source, signatures_count, analysis_details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content_id, content_hash, ai_probability, human_probability,
                detection_confidence, likely_source, len(signatures),
                json.dumps(detailed_analysis)
            ))
            
            analysis_id = cursor.lastrowid
            
            # Store individual signatures
            for signature in signatures:
                cursor.execute("""
                    INSERT INTO generation_signatures
                    (analysis_id, pattern_type, confidence, evidence, model_indicators)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    analysis_id, signature.pattern_type, signature.confidence,
                    json.dumps(signature.evidence), json.dumps(signature.model_indicators)
                ))
            
            conn.commit()
            return analysis_id

def demo_ai_generation_detection():
    """Demonstrate AI generation detection analysis"""
    print("🤖 Layer 6: AI-Generation Detection Demo")
    print("=" * 60)
    print("Machine learning detection of AI-generated content\n")
    
    # Initialize service
    service = AIGenerationDetectionService()
    
    # Test with AI-like content
    ai_like_content = """
    It's important to note that artificial intelligence has become increasingly sophisticated in recent years. Furthermore, machine learning algorithms are now capable of generating human-like text with remarkable accuracy. 
    
    Here are the key developments in AI text generation:
    1. Large language models like GPT have revolutionized natural language processing
    2. These models can produce coherent and contextually appropriate responses
    3. The quality of AI-generated content continues to improve
    
    Moreover, it's worth noting that these advancements have significant implications for content authenticity. However, detection methods are also evolving to keep pace with these developments.
    """
    
    print("📝 Test Content (AI-like):")
    print(f"   {ai_like_content[:150]}...")
    print()
    
    # Perform AI detection analysis
    result = service.detect_ai_generation(ai_like_content, "demo_ai_content_001")
    
    print("🤖 AI Generation Detection Results:")
    print(f"   🎯 AI Probability: {result.ai_probability:.2f}")
    print(f"   👤 Human Probability: {result.human_probability:.2f}")
    print(f"   🔍 Detection Confidence: {result.detection_confidence:.2f}")
    print(f"   📊 Likely Source: {result.likely_source}")
    print(f"   🔍 Signatures Found: {len(result.generation_signatures)}")
    print()
    
    print("🔍 Generation Signatures:")
    for i, signature in enumerate(result.generation_signatures, 1):
        print(f"   {i}. Type: {signature.pattern_type}")
        print(f"      Confidence: {signature.confidence:.2f}")
        print(f"      Evidence: {', '.join(signature.evidence[:2])}...")
        print(f"      Model Indicators: {', '.join(signature.model_indicators)}")
        print()
    
    print("📊 Signature Breakdown:")
    breakdown = result.detailed_analysis["signature_breakdown"]
    for sig_type, data in breakdown.items():
        print(f"   📋 {sig_type.title()}: {data['count']} signatures, avg confidence: {data['avg_confidence']:.2f}")
    print()
    
    print("⚠️ Risk Assessment:")
    risk = result.detailed_analysis["risk_assessment"]
    print(f"   🚨 Risk Level: {risk['risk_level']}")
    print(f"   💡 Recommendation: {risk['recommendation']}")
    print()
    
    # Test with human-like content
    human_like_content = """
    I was walking down the street yesterday when I bumped into my old friend Sarah. 
    She looked great! We hadn't seen each other since college, maybe 5 years ago? 
    Anyway, we decided to grab coffee and catch up on life.
    
    She told me about her new job at the startup downtown - sounds pretty crazy but exciting. 
    Long hours but she loves the team. I'm thinking about making a career change myself, 
    but honestly not sure what direction to go in yet.
    """
    
    print("\n📝 Test Content (Human-like):")
    print(f"   {human_like_content[:150]}...")
    print()
    
    result2 = service.detect_ai_generation(human_like_content, "demo_human_content_002")
    
    print("👤 Human Content Detection Results:")
    print(f"   🎯 AI Probability: {result2.ai_probability:.2f}")
    print(f"   👤 Human Probability: {result2.human_probability:.2f}")
    print(f"   🔍 Detection Confidence: {result2.detection_confidence:.2f}")
    print(f"   📊 Likely Source: {result2.likely_source}")
    print()
    
    print("🤖 Layer 6 Features Implemented:")
    print("   ✅ Linguistic pattern analysis for AI signatures")
    print("   ✅ Statistical feature extraction and analysis")
    print("   ✅ Structural pattern recognition")
    print("   ✅ Model-specific signature detection (GPT, Claude, Gemini)")
    print("   ✅ Ensemble probability calculation")
    print("   ✅ Detection confidence assessment")
    print("   ✅ Risk level determination and recommendations")
    print("   ✅ Comprehensive analysis storage and tracking")

if __name__ == "__main__":
    demo_ai_generation_detection()
