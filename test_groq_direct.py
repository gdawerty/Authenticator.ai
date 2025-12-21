import sys
import os
sys.path.insert(0, '/workspace/backend')

from services.groq_explanation_service import GroqExplanationService
import json

service = GroqExplanationService()
print(f"Service initialized. Available: {service.available}")
print(f"API Key present: {bool(service.api_key)}")
print(f"Model: {service.model}\n")

# Test 1: Simple prompt
print("="*80)
print("TEST 1: Simple prompt")
print("="*80)
test_prompt = "What is 2+2? Answer in one sentence."
print(f"Prompt: {test_prompt}")
result = service._call_groq(test_prompt, max_tokens=30)
print(f"Result: {result}\n")

# Test 2: Layer 1 explanation
print("="*80)
print("TEST 2: Layer 1 Classification")
print("="*80)
classification_result = {
    'result': 'text',
    'confidence': 0.97,
    'filename': 'research_paper.pdf',
    'file_type': 'PDF'
}
print(f"Input: {json.dumps(classification_result, indent=2)}")
result = service.generate_layer_1_explanation(classification_result)
print(f"Result: {result}\n")

# Test 3: Layer 2 Clone Detection
print("="*80)
print("TEST 3: Layer 2 Clone Detection")
print("="*80)
clone_result = {
    'similarity': 0.45,
    'matched_count': 3,
    'overlap': 15.2
}
print(f"Input: {json.dumps(clone_result, indent=2)}")
result = service.generate_layer_2_explanation(clone_result)
print(f"Result: {result}\n")
