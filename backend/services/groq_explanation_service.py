"""
Groq Cloud Integration Service
Uses Llama 3.3 70B through Groq Cloud API for generating layer explanations
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from groq import Groq as GroqClient
    GROQ_SDK_AVAILABLE = True
except ImportError:
    GROQ_SDK_AVAILABLE = False
    import requests

class GroqExplanationService:
    """Service to generate explanations for each analysis layer using Groq API"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq service with API key"""
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

        if not self.api_key:
            print("⚠️ Warning: GROQ_API_KEY not set. Explanations will be limited.")
            self.available = False
        else:
            self.available = True
            if GROQ_SDK_AVAILABLE:
                self.client = GroqClient(api_key=self.api_key)
                print("✅ Groq Classification Fallback initialized (SDK mode)")
            else:
                print("✅ Groq Classification Fallback initialized (HTTP mode)")

        self.base_url = "https://api.groq.com/openai/v1"

    def generate_layer_1_explanation(self, layer_result: Dict[str, Any]) -> str:
        """Generate explanation for Layer 1 - MIME Detection"""
        if not self.available:
            return self._fallback_layer_1(layer_result)

        # Extract actual data from layer result
        score = layer_result.get('score', 0)
        status = layer_result.get('status', 'unknown')
        details = layer_result.get('details', {})

        # Parse details if it's a string
        if isinstance(details, str):
            file_type = details.replace('File type: ', '').strip()
        else:
            file_type = details.get('file_type', 'unknown')

        prompt = f"""Based on this MIME detection result, provide a brief technical explanation:

MIME Detection Result:
- Score: {score:.0%}
- Status: {status}
- Detected File Type: {file_type}

Explain in 2-3 sentences:
1. What the MIME detection score indicates about file integrity
2. Whether the file type matches its extension
3. Any security concerns with this file type"""

        return self._call_groq(prompt)

    def generate_layer_2_explanation(self, layer_result: Dict[str, Any]) -> str:
        """Generate explanation for Layer 2 - BERT Classification"""
        if not self.available:
            return self._fallback_layer_2(layer_result)

        score = layer_result.get('score', 0)
        status = layer_result.get('status', 'unknown')
        details = layer_result.get('details', {})
        category = layer_result.get('category', 'unknown')

        # Parse details
        if isinstance(details, str):
            category_info = details
        else:
            category_info = details.get('category', category)

        prompt = f"""Based on this document classification result, provide a clear explanation:

Classification Result:
- Category: {category_info}
- Confidence Score: {score:.1%}
- Status: {status}

Explain in 2-3 sentences:
1. What this classification means for the document type
2. How confident the BERT model is in this classification
3. Whether this matches expected document characteristics"""

        return self._call_groq(prompt)

    def generate_layer_3_explanation(self, layer_result: Dict[str, Any]) -> str:
        """Generate explanation for Layer 3 - Clone Detection"""
        if not self.available:
            return self._fallback_layer_3(layer_result)

        score = layer_result.get('score', 0)
        status = layer_result.get('status', 'unknown')
        details = layer_result.get('details', {})

        # Parse details
        if isinstance(details, str):
            clone_info = details
        else:
            clone_info = str(details)

        prompt = f"""Based on this clone detection analysis, explain what was found:

Clone Detection Result:
- Originality Score: {score:.0%}
- Status: {status}
- Details: {clone_info}

Explain in 2-3 sentences:
1. Whether any plagiarism or cloning was detected
2. What the originality score indicates
3. Whether this document appears to be unique"""

        return self._call_groq(prompt)

    def generate_layer_4_explanation(self, layer_result: Dict[str, Any]) -> str:
        """Generate explanation for Layer 4 - Cryptographic Validation"""
        if not self.available:
            return self._fallback_layer_4(layer_result)

        score = layer_result.get('score', 0)
        status = layer_result.get('status', 'unknown')
        details = layer_result.get('details', {})

        # Parse details
        if isinstance(details, str):
            crypto_info = details
        else:
            crypto_info = str(details)

        prompt = f"""Based on this cryptographic validation result, explain the security assessment:

Cryptographic Validation Result:
- Integrity Score: {score:.0%}
- Status: {status}
- Details: {crypto_info}

Explain in 2-3 sentences:
1. Whether the file hash verification passed
2. What this means for document integrity
3. Whether there are signs of tampering or alteration"""

        return self._call_groq(prompt)

    def generate_layer_5_explanation(self, layer_result: Dict[str, Any]) -> str:
        """Generate explanation for Layer 5 - RAG Factuality Analysis"""
        if not self.available:
            return self._fallback_layer_5(layer_result)

        score = layer_result.get('score', 0)
        status = layer_result.get('status', 'unknown')
        details = layer_result.get('details', {})

        # Parse details
        if isinstance(details, str):
            rag_info = details
        elif isinstance(details, dict):
            claims = details.get('claims_analyzed', 0)
            verdict = details.get('verdict', 'unknown')
            rag_info = f"Claims analyzed: {claims}, Verdict: {verdict}"
        else:
            rag_info = str(details)

        prompt = f"""Based on this RAG factuality analysis, explain the findings:

RAG Analysis Result:
- Factuality Score: {score:.0%}
- Status: {status}
- Analysis: {rag_info}

Explain in 2-3 sentences:
1. How well the document content aligns with verified sources
2. Whether factual claims were validated
3. Any concerns about accuracy or misinformation"""

        return self._call_groq(prompt)

    def generate_layer_6_explanation(self, layer_result: Dict[str, Any]) -> str:
        """Generate explanation for Layer 6 - AI Content Detection"""
        if not self.available:
            return self._fallback_layer_6(layer_result)

        score = layer_result.get('score', 0)
        status = layer_result.get('status', 'unknown')
        details = layer_result.get('details', {})

        # Parse AI detection specifics
        if isinstance(details, dict):
            ai_prob = details.get('ai_probability', score)
            human_prob = details.get('human_probability', 1 - score)
            text_length = details.get('text_length', 0)
        elif isinstance(details, str):
            # Parse from string like "90.0% human, 10.0% AI"
            ai_prob = score
            human_prob = 1 - score
            text_length = 0
        else:
            ai_prob = score
            human_prob = 1 - score
            text_length = 0

        prompt = f"""Based on this AI content detection analysis, explain the authorship assessment:

AI Detection Result:
- AI Probability: {ai_prob:.1%}
- Human Probability: {human_prob:.1%}
- Text Analyzed: {text_length} characters
- Status: {status}

Explain in 2-3 sentences:
1. Whether the content appears to be AI-generated or human-written
2. What patterns indicate the authorship type
3. Confidence level in this assessment"""

        return self._call_groq(prompt)

    def generate_comprehensive_explanation(self, final_result: Dict[str, Any]) -> str:
        """Generate comprehensive explanation for Layer 7 - Final Assessment"""
        if not self.available:
            return self._fallback_comprehensive(final_result)

        # Extract data from the final result structure
        # This could be either the full analysis result or just the layer 7 data

        if 'layer_summary' in final_result:
            # It's the full final prediction result
            layer_summary = final_result.get('layer_summary', {})
            final_score = final_result.get('authenticity_score', 0)
            confidence = final_result.get('confidence', 0)
        else:
            # It's individual layer data
            layer_summary = final_result
            final_score = final_result.get('score', 0)
            confidence = final_result.get('confidence', 0)

        # Build summary of all layers
        layers_text = []
        for layer_name, layer_data in layer_summary.items():
            if isinstance(layer_data, dict):
                score = layer_data.get('score', 0)
                layers_text.append(f"- {layer_name}: {score:.1%}")

        layers_summary = "\n".join(layers_text) if layers_text else "No layer data available"

        prompt = f"""Based on this comprehensive 7-layer document authenticity analysis, provide a final assessment:

Final Analysis Summary:
{layers_summary}

Overall Authenticity Score: {final_score:.1%}
Confidence: {confidence:.1%}

Provide a comprehensive explanation (3-4 sentences) that:
1. Summarizes the overall authenticity determination
2. Identifies the most concerning findings across all layers
3. Provides a clear recommendation about the document's trustworthiness
4. Notes any layers that strongly support or contradict authenticity"""

        return self._call_groq(prompt, max_tokens=250)

    # Fallback methods when GROQ is not available
    def _fallback_layer_1(self, layer_result: Dict[str, Any]) -> str:
        score = layer_result.get('score', 0)
        details = layer_result.get('details', 'unknown')
        if isinstance(details, str):
            file_type = details.replace('File type: ', '')
        else:
            file_type = str(details)
        return f"MIME detection completed with {score:.0%} confidence. File type identified as {file_type}."

    def _fallback_layer_2(self, layer_result: Dict[str, Any]) -> str:
        score = layer_result.get('score', 0)
        category = layer_result.get('category', layer_result.get('details', 'unknown'))
        return f"Document classified as '{category}' with {score:.1%} confidence by BERT model."

    def _fallback_layer_3(self, layer_result: Dict[str, Any]) -> str:
        score = layer_result.get('score', 0)
        return f"Clone detection shows {score:.0%} originality score. No significant plagiarism detected."

    def _fallback_layer_4(self, layer_result: Dict[str, Any]) -> str:
        score = layer_result.get('score', 0)
        details = layer_result.get('details', '')
        return f"Cryptographic validation score: {score:.0%}. {details}"

    def _fallback_layer_5(self, layer_result: Dict[str, Any]) -> str:
        score = layer_result.get('score', 0)
        details = layer_result.get('details', '')
        return f"RAG factuality score: {score:.0%}. {details}"

    def _fallback_layer_6(self, layer_result: Dict[str, Any]) -> str:
        score = layer_result.get('score', 0)
        human_prob = 1 - score
        return f"AI detection indicates {human_prob:.1%} human authorship, {score:.1%} AI-generated probability."

    def _fallback_comprehensive(self, final_result: Dict[str, Any]) -> str:
        score = final_result.get('authenticity_score', final_result.get('score', 0))
        if score > 0.75:
            return f"High authenticity score of {score:.1%}. Document appears genuine with strong validation across all layers."
        elif score > 0.5:
            return f"Moderate authenticity score of {score:.1%}. Some concerns detected but document may still be valid."
        else:
            return f"Low authenticity score of {score:.1%}. Multiple layers indicate potential issues with document authenticity."

    def _call_groq(self, prompt: str, max_tokens: int = 150) -> str:
        """Call Groq API to generate explanation"""
        if not self.available:
            return "Groq API not configured"

        try:
            if GROQ_SDK_AVAILABLE:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a document authenticity expert. Provide clear, technical explanations of analysis results. Be concise and factual."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model=self.model,
                    temperature=0.3,
                    max_tokens=max_tokens,
                    top_p=0.9
                )
                return chat_completion.choices[0].message.content.strip()
            else:
                import requests
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a document authenticity expert. Provide clear, technical explanations of analysis results. Be concise and factual."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": max_tokens,
                    "top_p": 0.9
                }

                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=15
                )

                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    print(f"⚠️ Groq API error: {response.status_code} - {response.text}")
                    return "Unable to generate explanation due to API error"

        except Exception as e:
            print(f"⚠️ Error calling Groq API: {e}")
            return f"Error generating explanation: {str(e)}"


# Singleton instance
_groq_service = None

def get_groq_service(api_key: Optional[str] = None) -> GroqExplanationService:
    """Get or create Groq service singleton"""
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqExplanationService(api_key)
    return _groq_service
