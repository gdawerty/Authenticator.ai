"""
Highlight Mapping Service for Authenticator.AI
Implements NLP diff engine for phrase-level authenticity analysis with offset mapping
"""

import re
import json
import difflib
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import hashlib

# Try to import NLTK with graceful fallback
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    
    # Download required NLTK data with error handling
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        try:
            nltk.download('punkt')
        except:
            pass
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        try:
            nltk.download('stopwords')
        except:
            pass
    
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

# Fallback implementations
def fallback_sent_tokenize(text: str) -> List[str]:
    """Fallback sentence tokenization using simple rules"""
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]

def fallback_word_tokenize(text: str) -> List[str]:
    """Fallback word tokenization using simple rules"""
    words = re.findall(r'\b\w+\b', text.lower())
    return words

def fallback_stopwords() -> set:
    """Fallback English stopwords"""
    return {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
        'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
        'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
        'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
        'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
        'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
        'further', 'then', 'once'
    }

@dataclass
class Highlight:
    """Represents a highlighted text segment with confidence and reasoning"""
    start: int
    end: int
    text: str
    confidence: float
    layer_source: str
    issue_type: str
    severity: str
    color: str
    explanation: str
    details: Dict[str, Any]

@dataclass
class TextSegment:
    """Represents a text segment with analysis metadata"""
    start: int
    end: int
    text: str
    sentence_index: int
    phrase_index: int
    tokens: List[str]
    authenticity_scores: Dict[str, float]
    flagged_issues: List[str]

class HighlightMappingService:
    """
    Service for mapping analysis results to specific text locations with highlights
    """
    
    def __init__(self):
        if NLTK_AVAILABLE:
            try:
                self.stop_words = set(stopwords.words('english'))
                self.sent_tokenize = sent_tokenize
                self.word_tokenize = word_tokenize
            except:
                # Fallback if NLTK data is not available
                self.stop_words = fallback_stopwords()
                self.sent_tokenize = fallback_sent_tokenize
                self.word_tokenize = fallback_word_tokenize
        else:
            self.stop_words = fallback_stopwords()
            self.sent_tokenize = fallback_sent_tokenize
            self.word_tokenize = fallback_word_tokenize
            
        self.severity_colors = {
            'critical': '#ff4444',  # Red
            'warning': '#ffaa00',   # Orange
            'info': '#4488ff',      # Blue
            'success': '#44ff44'    # Green
        }
    
    def analyze_document_phrases(self, text: str, layer_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze document text and generate phrase-level authenticity mapping
        """
        # Split text into analyzable segments
        segments = self._segment_text(text)
        
        # Analyze each segment for authenticity indicators
        analyzed_segments = []
        highlights = []
        
        for segment in segments:
            # Calculate authenticity scores for this segment
            segment_scores = self._calculate_segment_scores(segment, layer_results)
            segment.authenticity_scores = segment_scores
            
            # Generate highlights for flagged content
            segment_highlights = self._generate_segment_highlights(segment, layer_results)
            highlights.extend(segment_highlights)
            
            analyzed_segments.append(segment)
        
        # Calculate overall document authenticity
        overall_score = self._calculate_overall_score(analyzed_segments)
        
        return {
            'document_text': text,
            'overall_authenticity': overall_score,
            'segments': [self._segment_to_dict(seg) for seg in analyzed_segments],
            'highlights': [self._highlight_to_dict(h) for h in highlights],
            'analysis_metadata': {
                'total_segments': len(analyzed_segments),
                'flagged_segments': len([s for s in analyzed_segments if s.flagged_issues]),
                'highlight_count': len(highlights),
                'processing_timestamp': self._get_timestamp()
            }
        }
    
    def _segment_text(self, text: str) -> List[TextSegment]:
        """Split text into analyzable segments (sentences and phrases)"""
        segments = []
        
        # Tokenize into sentences
        sentences = self.sent_tokenize(text)
        current_offset = 0
        
        for sent_idx, sentence in enumerate(sentences):
            # Find the actual position of the sentence in the original text
            sent_start = text.find(sentence, current_offset)
            sent_end = sent_start + len(sentence)
            
            # Split sentence into phrases (by punctuation and conjunctions)
            phrases = self._split_into_phrases(sentence)
            phrase_offset = sent_start
            
            for phrase_idx, phrase in enumerate(phrases):
                # Find phrase position within sentence
                phrase_start = text.find(phrase.strip(), phrase_offset)
                phrase_end = phrase_start + len(phrase.strip())
                
                # Tokenize phrase
                tokens = self.word_tokenize(phrase.strip().lower())
                tokens = [t for t in tokens if t.isalnum() and t not in self.stop_words]
                
                if tokens:  # Only add segments with meaningful tokens
                    segment = TextSegment(
                        start=phrase_start,
                        end=phrase_end,
                        text=phrase.strip(),
                        sentence_index=sent_idx,
                        phrase_index=phrase_idx,
                        tokens=tokens,
                        authenticity_scores={},
                        flagged_issues=[]
                    )
                    segments.append(segment)
                
                phrase_offset = phrase_end
            
            current_offset = sent_end
        
        return segments
    
    def _split_into_phrases(self, sentence: str) -> List[str]:
        """Split sentence into meaningful phrases"""
        # Split by common phrase boundaries
        phrase_patterns = [
            r'[.!?]+',  # End of sentence punctuation
            r'[,;:]+',  # Clause separators
            r'\s+(?:and|or|but|however|therefore|thus|moreover|furthermore|nevertheless)\s+',  # Conjunctions
            r'\s+(?:because|since|if|when|while|although|though|unless)\s+',  # Subordinating conjunctions
        ]
        
        phrases = [sentence]
        
        for pattern in phrase_patterns:
            new_phrases = []
            for phrase in phrases:
                split_phrases = re.split(pattern, phrase)
                new_phrases.extend([p.strip() for p in split_phrases if p.strip()])
            phrases = new_phrases
        
        # Filter out very short phrases (less than 3 words)
        meaningful_phrases = []
        for phrase in phrases:
            word_count = len(phrase.split())
            if word_count >= 3:
                meaningful_phrases.append(phrase)
            elif word_count >= 1 and len(meaningful_phrases) > 0:
                # Append short phrases to the previous phrase
                meaningful_phrases[-1] += ' ' + phrase
        
        return meaningful_phrases if meaningful_phrases else [sentence]
    
    def _calculate_segment_scores(self, segment: TextSegment, layer_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate authenticity scores for a text segment based on layer results"""
        scores = {}
        
        # MIME Detection - document-level only
        scores['mime'] = layer_results.get('layer1', {}).get('score', 1.0)
        
        # Classification - check if segment contains classified terms
        classification_score = layer_results.get('layer2', {}).get('score', 1.0)
        classification_details = layer_results.get('layer2', {}).get('details', {})
        
        # Look for classification indicators in segment
        if self._contains_classification_indicators(segment.text, classification_details):
            scores['classification'] = max(0.0, classification_score - 0.2)  # Reduce score for flagged content
        else:
            scores['classification'] = classification_score
        
        # Clone Detection - check for similarity patterns
        clone_score = layer_results.get('layer3', {}).get('score', 1.0)
        if self._contains_clone_patterns(segment.text, layer_results.get('layer3', {})):
            scores['clone'] = max(0.0, clone_score - 0.3)
        else:
            scores['clone'] = clone_score
        
        # Cryptographic - document-level only
        scores['cryptographic'] = layer_results.get('layer4', {}).get('score', 1.0)
        
        # RAG Analysis - context-aware scoring
        scores['rag'] = layer_results.get('layer5', {}).get('score', 0.8)  # Default for not implemented
        
        # AI Detection - check for AI-generated patterns
        ai_score = layer_results.get('layer6', {}).get('score', 1.0)
        if self._contains_ai_patterns(segment.text):
            scores['ai_detection'] = max(0.0, ai_score - 0.4)
        else:
            scores['ai_detection'] = ai_score
        
        # Final prediction - weighted average
        weights = {'mime': 0.1, 'classification': 0.15, 'clone': 0.2, 'cryptographic': 0.1, 'rag': 0.15, 'ai_detection': 0.3}
        scores['final'] = sum(scores[layer] * weight for layer, weight in weights.items())
        
        return scores
    
    def _contains_classification_indicators(self, text: str, classification_details: Dict[str, Any]) -> bool:
        """Check if text contains classification-related flags"""
        # Check for specific terms that might indicate issues
        suspicious_terms = ['generated', 'artificial', 'automated', 'bot', 'ai', 'gpt', 'model']
        text_lower = text.lower()
        
        return any(term in text_lower for term in suspicious_terms)
    
    def _contains_clone_patterns(self, text: str, clone_results: Dict[str, Any]) -> bool:
        """Check if text contains clone detection patterns"""
        # Look for exact matches or high similarity phrases
        clone_matches = clone_results.get('similar_documents', [])
        
        for match in clone_matches:
            if match.get('similarity_score', 0) > 0.8:
                return True
        
        return False
    
    def _contains_ai_patterns(self, text: str) -> bool:
        """Check if text contains AI-generated content patterns"""
        ai_indicators = [
            r'\b(?:as an ai|i am an ai|as a language model|i\'m sorry, but i cannot)\b',
            r'\bgenerated by\b',
            r'\bcertainly[!.]\s',
            r'\babsolutely[!.]\s',
            r'\bin conclusion,\s',
            r'\bto summarize,\s',
            r'\bit\'s important to note that\b',
            r'\bit\'s worth noting that\b'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in ai_indicators)
    
    def _generate_segment_highlights(self, segment: TextSegment, layer_results: Dict[str, Any]) -> List[Highlight]:
        """Generate highlights for a text segment based on analysis results"""
        highlights = []
        
        # Get flagged content from layer results
        flagged_content = layer_results.get('flagged_content', [])
        
        for flag in flagged_content:
            # Check if this flag applies to the current segment
            if self._flag_applies_to_segment(flag, segment):
                highlight = self._create_highlight(flag, segment)
                if highlight:
                    highlights.append(highlight)
        
        # Generate AI pattern highlights
        ai_highlights = self._generate_ai_pattern_highlights(segment)
        highlights.extend(ai_highlights)
        
        return highlights
    
    def _flag_applies_to_segment(self, flag: Dict[str, Any], segment: TextSegment) -> bool:
        """Check if a flagged content item applies to the current segment"""
        # For now, apply flags based on layer and content type
        # This could be enhanced with more sophisticated matching
        
        flag_type = flag.get('type', '')
        segment_text_lower = segment.text.lower()
        
        # AI detection flags
        if flag_type == 'ai_generated_content':
            return self._contains_ai_patterns(segment.text)
        
        # Clone detection flags
        if flag_type == 'clone_detected':
            return 'similar' in segment_text_lower or 'duplicate' in segment_text_lower
        
        # Classification flags
        if flag_type == 'suspicious_classification':
            return self._contains_classification_indicators(segment.text, {})
        
        return False
    
    def _create_highlight(self, flag: Dict[str, Any], segment: TextSegment) -> Optional[Highlight]:
        """Create a highlight object from a flag and segment"""
        severity = flag.get('severity', 'info')
        color = self.severity_colors.get(severity, '#888888')
        
        return Highlight(
            start=segment.start,
            end=segment.end,
            text=segment.text,
            confidence=1.0 - segment.authenticity_scores.get('final', 0.5),
            layer_source=flag.get('layer_name', 'Unknown'),
            issue_type=flag.get('type', 'unknown'),
            severity=severity,
            color=color,
            explanation=flag.get('message', 'Issue detected'),
            details=flag.get('details', {})
        )
    
    def _generate_ai_pattern_highlights(self, segment: TextSegment) -> List[Highlight]:
        """Generate highlights for AI-generated patterns in text"""
        highlights = []
        
        ai_patterns = [
            (r'\b(?:as an ai|i am an ai|as a language model)\b', 'AI self-reference detected'),
            (r'\bcertainly[!.]\s', 'AI confirmation pattern'),
            (r'\babsolutely[!.]\s', 'AI emphasis pattern'),
            (r'\bin conclusion,\s', 'AI summarization pattern'),
            (r'\bit\'s important to note that\b', 'AI cautionary pattern')
        ]
        
        for pattern, explanation in ai_patterns:
            matches = list(re.finditer(pattern, segment.text, re.IGNORECASE))
            
            for match in matches:
                highlight = Highlight(
                    start=segment.start + match.start(),
                    end=segment.start + match.end(),
                    text=match.group(),
                    confidence=0.8,
                    layer_source='AI Detection',
                    issue_type='ai_pattern',
                    severity='warning',
                    color=self.severity_colors['warning'],
                    explanation=explanation,
                    details={'pattern': pattern, 'match_position': match.span()}
                )
                highlights.append(highlight)
        
        return highlights
    
    def _calculate_overall_score(self, segments: List[TextSegment]) -> float:
        """Calculate overall document authenticity score"""
        if not segments:
            return 0.5
        
        # Weight segments by length
        total_chars = sum(len(seg.text) for seg in segments)
        weighted_score = 0.0
        
        for segment in segments:
            weight = len(segment.text) / total_chars
            segment_score = segment.authenticity_scores.get('final', 0.5)
            weighted_score += segment_score * weight
        
        return weighted_score
    
    def _segment_to_dict(self, segment: TextSegment) -> Dict[str, Any]:
        """Convert TextSegment to dictionary"""
        return {
            'start': segment.start,
            'end': segment.end,
            'text': segment.text,
            'sentence_index': segment.sentence_index,
            'phrase_index': segment.phrase_index,
            'tokens': segment.tokens,
            'authenticity_scores': segment.authenticity_scores,
            'flagged_issues': segment.flagged_issues
        }
    
    def _highlight_to_dict(self, highlight: Highlight) -> Dict[str, Any]:
        """Convert Highlight to dictionary"""
        return {
            'start': highlight.start,
            'end': highlight.end,
            'text': highlight.text,
            'confidence': highlight.confidence,
            'layer_source': highlight.layer_source,
            'issue_type': highlight.issue_type,
            'severity': highlight.severity,
            'color': highlight.color,
            'explanation': highlight.explanation,
            'details': highlight.details
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def generate_document_highlights_api(self, document_id: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate highlights for API endpoint
        """
        document_text = analysis_results.get('document_text', '')
        layer_results = analysis_results.get('layer_results', {})
        
        if not document_text:
            return {
                'document_id': document_id,
                'highlights': [],
                'error': 'Document text not found'
            }
        
        # Analyze document and generate highlights
        analysis = self.analyze_document_phrases(document_text, layer_results)
        
        return {
            'document_id': document_id,
            'document_text': document_text,
            'highlights': analysis['highlights'],
            'segments': analysis['segments'],
            'overall_authenticity': analysis['overall_authenticity'],
            'metadata': analysis['analysis_metadata']
        }

# Global service instance
highlight_service = HighlightMappingService()
