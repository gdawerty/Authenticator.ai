import requests
import json
import time

BASE_URL = 'http://localhost:8001/api/explanations'

print("\n" + "="*80)
print("🧪 GROQ EXPLANATION SERVICE - FULL LAYER TEST")
print("="*80)

# Test health
print("\n🏥 Health Check...")
resp = requests.get(f'{BASE_URL}/health', timeout=10)
health_data = resp.json()
print(f"✅ Status: {health_data['status']}")
print(f"✅ Model: {health_data['model']}")
print(f"✅ API Configured: {health_data['api_configured']}\n")

# Layer 1: Classification
print("="*80)
print("📊 LAYER 1: CLASSIFICATION")
print("="*80)
payload = {
    "layer_result": {
        "result": "text",
        "confidence": 0.97,
        "filename": "research_paper.pdf",
        "file_type": "PDF",
        "encoding": "UTF-8",
        "size_kb": 245
    }
}
resp = requests.post(f'{BASE_URL}/layer/1', json=payload, timeout=30)
data = resp.json()
print(f"Status: {data['status']}")
print(f"Layer: {data['layer']}")
print(f"\n📝 Explanation:\n{data['explanation']}\n")
time.sleep(2)

# Layer 2: Clone Detection
print("="*80)
print("📊 LAYER 2: CLONE DETECTION")
print("="*80)
payload = {
    "layer_result": {
        "similarity_score": 0.45,
        "plagiarism_percentage": 15.2,
        "matched_documents": 3,
        "high_similarity_sections": 2,
        "status": "low_plagiarism"
    }
}
resp = requests.post(f'{BASE_URL}/layer/2', json=payload, timeout=30)
data = resp.json()
print(f"Status: {data['status']}")
print(f"Layer: {data['layer']}")
print(f"\n📝 Explanation:\n{data['explanation']}\n")
time.sleep(2)

# Layer 3: Cryptographic Verification
print("="*80)
print("📊 LAYER 3: CRYPTOGRAPHIC VERIFICATION")
print("="*80)
payload = {
    "layer_result": {
        "hash_verification": "valid",
        "signature_status": "verified",
        "certificate_chain": "trusted",
        "timestamp_valid": True,
        "tampering_detected": False,
        "algorithm": "SHA-256"
    }
}
resp = requests.post(f'{BASE_URL}/layer/3', json=payload, timeout=30)
data = resp.json()
print(f"Status: {data['status']}")
print(f"Layer: {data['layer']}")
print(f"\n📝 Explanation:\n{data['explanation']}\n")
time.sleep(2)

# Layer 4: RAG Context
print("="*80)
print("📊 LAYER 4: RAG CONTEXT")
print("="*80)
payload = {
    "layer_result": {
        "retrieval_score": 0.92,
        "source_alignment": 0.88,
        "factual_accuracy": 0.85,
        "context_match": True,
        "relevant_documents_found": 5,
        "confidence_level": "high"
    }
}
resp = requests.post(f'{BASE_URL}/layer/4', json=payload, timeout=30)
data = resp.json()
print(f"Status: {data['status']}")
print(f"Layer: {data['layer']}")
print(f"\n📝 Explanation:\n{data['explanation']}\n")
time.sleep(2)

# Layer 5: Authenticity Scoring
print("="*80)
print("📊 LAYER 5: AUTHENTICITY SCORING")
print("="*80)
payload = {
    "layer_result": {
        "authenticity_score": 87.5,
        "score_interpretation": "Highly Authentic",
        "contributing_factors": [
            "verified_source",
            "consistent_style",
            "no_tampering",
            "proper_signature"
        ],
        "confidence": 0.94
    }
}
resp = requests.post(f'{BASE_URL}/layer/5', json=payload, timeout=30)
data = resp.json()
print(f"Status: {data['status']}")
print(f"Layer: {data['layer']}")
print(f"\n📝 Explanation:\n{data['explanation']}\n")
time.sleep(2)

# Layer 6: AI Detection
print("="*80)
print("📊 LAYER 6: AI DETECTION")
print("="*80)
payload = {
    "layer_result": {
        "ai_probability": 0.08,
        "writing_style": "human",
        "pattern_detection": "natural_language",
        "entropy_score": 0.72,
        "ai_generated": False,
        "confidence": 0.91
    }
}
resp = requests.post(f'{BASE_URL}/layer/6', json=payload, timeout=30)
data = resp.json()
print(f"Status: {data['status']}")
print(f"Layer: {data['layer']}")
print(f"\n📝 Explanation:\n{data['explanation']}\n")
time.sleep(2)

# Comprehensive Explanation
print("="*80)
print("🎯 COMPREHENSIVE EXPLANATION")
print("="*80)
payload = {
    "analysis_result": {
        "filename": "research_paper.pdf",
        "final_score": 87.5,
        "classification": "Authentic",
        "layers_completed": 6,
        "overall_confidence": 0.89,
        "timestamp": "2025-10-26T10:30:00Z"
    }
}
resp = requests.post(f'{BASE_URL}/comprehensive', json=payload, timeout=30)
data = resp.json()
print(f"Status: {data['status']}")
print(f"\n📝 Comprehensive Summary:\n{data['comprehensive_explanation']}\n")

print("="*80)
print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
print("="*80 + "\n")
