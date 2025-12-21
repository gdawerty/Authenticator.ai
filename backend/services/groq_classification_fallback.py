"""
Groq-based Fallback Classification Service
When VIT or BERT confidence is low, use Groq to assist with classification
Uses HTTP API by default, falls back to SDK if available
"""

import os
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from groq import Groq as GroqClient
    GROQ_SDK_AVAILABLE = True
except ImportError:
    GROQ_SDK_AVAILABLE = False

class GroqClassificationFallback:
    """Fallback to Groq when confidence scores are low"""
    
    _instance = None
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.api_key = os.getenv('GROQ_API_KEY')
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.confidence_threshold = float(os.getenv('GROQ_FALLBACK_THRESHOLD', '0.60'))
        
        if self.api_key:
            self.available = True
            # Try SDK first, fall back to HTTP
            if GROQ_SDK_AVAILABLE:
                try:
                    self.client = GroqClient(api_key=self.api_key)
                    self.use_sdk = True
                    print("✅ Groq Classification Fallback initialized (SDK mode)")
                except Exception as e:
                    print(f"⚠️ Groq SDK failed, using HTTP mode: {e}")
                    self.use_sdk = False
            else:
                self.use_sdk = False
                print("✅ Groq Classification Fallback initialized (HTTP mode)")
        else:
            self.available = False
            print("⚠️ Groq Classification Fallback not available - GROQ_API_KEY not set")
        
        self._initialized = True
    
    def should_use_fallback(self, confidence: float) -> bool:
        """Check if confidence is below threshold"""
        return self.available and confidence < self.confidence_threshold
    
    def _call_groq_http(self, messages: list) -> str:
        """Call Groq via HTTP API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 300,
                "top_p": 0.9
            }
            
            response = requests.post(self.GROQ_API_URL, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            return result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
        except Exception as e:
            print(f"⚠️ Groq HTTP API error: {e}")
            return ""
    
    def _call_groq_sdk(self, messages: list) -> str:
        """Call Groq via SDK"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.3,
                max_tokens=300,
                top_p=0.9
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Groq SDK error: {e}")
            return ""
    
    def _call_groq(self, messages: list) -> str:
        """Call Groq API (SDK or HTTP)"""
        if self.use_sdk:
            return self._call_groq_sdk(messages)
        else:
            return self._call_groq_http(messages)
    
    def classify_with_groq(self, content_preview: str, original_predictions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Groq to help classify when confidence is low
        
        Args:
            content_preview: Preview of the content to classify
            original_predictions: Original VIT/BERT predictions
            
        Returns:
            Enhanced classification with Groq reasoning
        """
        if not self.available:
            return {"status": "fallback_unavailable"}
        
        try:
            # Build context from original predictions
            vit_result = original_predictions.get('vit', {})
            bert_result = original_predictions.get('bert', {})
            
            prompt = f"""Based on the following content analysis, provide a confident classification:

Content Preview:
{content_preview[:500]}

Original Classifications:
- VIT Model: {vit_result.get('predicted_class', 'Unknown')} (Confidence: {vit_result.get('confidence', 0):.2%})
- BERT Model: {bert_result.get('predicted_class', 'Unknown')} (Confidence: {bert_result.get('confidence', 0):.2%})

Please provide:
1. Your best classification based on the content
2. Confidence level (0-100%)
3. Key indicators that led to this classification
4. Recommended class (text, image, hybrid, unknown)

Format your response as JSON."""

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert document classifier. Analyze content and provide confident classifications."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response_text = self._call_groq(messages)
            
            if not response_text:
                return {"status": "fallback_failed", "error": "Groq API returned empty response"}
            
            # Parse Groq response
            try:
                groq_result = json.loads(response_text)
            except:
                groq_result = {"reasoning": response_text}
            
            # Build enhanced result
            result = {
                "status": "fallback_classification",
                "original_vit": vit_result,
                "original_bert": bert_result,
                "groq_fallback": {
                    "classification": groq_result.get("recommended_class", "unknown"),
                    "confidence": groq_result.get("confidence", 50) / 100.0,
                    "reasoning": groq_result.get("reasoning", "Classification assisted by Groq"),
                    "indicators": groq_result.get("key_indicators", []),
                    "timestamp": datetime.utcnow().isoformat()
                },
                "model": "groq-fallback-ensemble",
                "fallback_reason": "Low confidence in primary models"
            }
            
            print(f"✅ Groq fallback classification: {result['groq_fallback']['classification']}")
            return result
            
        except Exception as e:
            print(f"⚠️ Groq fallback classification error: {e}")
            vit_result = original_predictions.get('vit', {})
            bert_result = original_predictions.get('bert', {})
            return {
                "status": "fallback_failed",
                "original_vit": vit_result,
                "original_bert": bert_result,
                "error": str(e)
            }
    
    def enhance_classification(self, classification_result: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        """
        Enhance classification with Groq if confidence is low
        
        Args:
            classification_result: Original classification result
            confidence: Confidence score from primary model
            
        Returns:
            Enhanced or original classification
        """
        if not self.should_use_fallback(confidence):
            return classification_result
        
        print(f"⚠️ Low confidence ({confidence:.2%}) detected. Using Groq fallback...")
        
        # Get content preview if available
        content_preview = classification_result.get('content_preview', '')
        if not content_preview:
            content_preview = classification_result.get('filename', 'Unknown document')
        
        # Prepare original predictions for context
        original_predictions = {
            'vit': {
                'predicted_class': classification_result.get('result', 'unknown'),
                'confidence': confidence
            },
            'bert': classification_result.get('bert_result', {})
        }
        
        # Get Groq fallback
        fallback_result = self.classify_with_groq(content_preview, original_predictions)
        
        # Merge results
        enhanced = classification_result.copy()
        enhanced['fallback_used'] = True
        enhanced['groq_fallback'] = fallback_result.get('groq_fallback', {})
        
        if fallback_result.get('groq_fallback'):
            # Use Groq classification if it has higher confidence
            groq_conf = fallback_result['groq_fallback'].get('confidence', 0)
            if groq_conf > confidence:
                enhanced['result'] = fallback_result['groq_fallback']['classification']
                enhanced['confidence'] = groq_conf
                enhanced['used_fallback_classification'] = True
                print(f"✅ Using Groq classification: {enhanced['result']} ({groq_conf:.2%})")
        
        return enhanced

# Singleton getter
def get_groq_fallback():
    """Get or create the Groq Classification Fallback service"""
    return GroqClassificationFallback()
