#!/usr/bin/env python3
"""
Test all Groq explanation layers with sample data
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001/api/explanations"

def print_response(title, response):
    """Print formatted response"""
    print(f"\n{'='*80}")
    print(f"✨ {title}")
    print(f"{'='*80}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(f"Status: {response.status_code}")
        print(response.text)

def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print_response("Health Check", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_layer_1():
    """Test Layer 1: Classification"""
    print("\n📊 Testing Layer 1: Classification")
    payload = {
        "layer_result": {
            "result": "text",
            "confidence": 0.97,
            "filename": "document.pdf",
            "file_type": "PDF",
            "encoding": "UTF-8",
            "size_kb": 245
        }
    }
    try:
        response = requests.post(f"{BASE_URL}/layer/1", json=payload, timeout=30)
        print_response("Layer 1 - Classification Explanation", response)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_layer_2():
    """Test Layer 2: Clone Detection"""
    print("\n📊 Testing Layer 2: Clone Detection")
    payload = {
        "layer_result": {
            "similarity_score": 0.45,
            "plagiarism_percentage": 15.2,
            "matched_documents": 3,
            "high_similarity_sections": 2,
            "status": "low_plagiarism"
        }
    }
    try:
        response = requests.post(f"{BASE_URL}/layer/2", json=payload, timeout=30)
        print_response("Layer 2 - Clone Detection Explanation", response)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_layer_3():
    """Test Layer 3: Cryptographic Verification"""
    print("\n📊 Testing Layer 3: Cryptographic Verification")
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
    try:
        response = requests.post(f"{BASE_URL}/layer/3", json=payload, timeout=30)
        print_response("Layer 3 - Cryptographic Verification Explanation", response)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_layer_4():
    """Test Layer 4: RAG Context"""
    print("\n📊 Testing Layer 4: RAG Context")
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
    try:
        response = requests.post(f"{BASE_URL}/layer/4", json=payload, timeout=30)
        print_response("Layer 4 - RAG Context Explanation", response)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_layer_5():
    """Test Layer 5: Authenticity Scoring"""
    print("\n📊 Testing Layer 5: Authenticity Scoring")
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
    try:
        response = requests.post(f"{BASE_URL}/layer/5", json=payload, timeout=30)
        print_response("Layer 5 - Authenticity Scoring Explanation", response)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_layer_6():
    """Test Layer 6: AI Detection"""
    print("\n📊 Testing Layer 6: AI Detection")
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
    try:
        response = requests.post(f"{BASE_URL}/layer/6", json=payload, timeout=30)
        print_response("Layer 6 - AI Detection Explanation", response)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_comprehensive():
    """Test Comprehensive Explanation"""
    print("\n🎯 Testing Comprehensive Explanation")
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
    try:
        response = requests.post(f"{BASE_URL}/comprehensive", json=payload, timeout=30)
        print_response("Comprehensive Explanation", response)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "🧪 GROQ EXPLANATION SERVICE - FULL TEST" + " "*20 + "║")
    print("║" + " "*15 + "Testing All 6 Layers + Comprehensive Explanation" + " "*17 + "║")
    print("╚" + "="*78 + "╝")
    
    results = {}
    
    # Test health
    results['health'] = test_health()
    time.sleep(2)
    
    # Test each layer
    results['layer_1'] = test_layer_1()
    time.sleep(2)
    
    results['layer_2'] = test_layer_2()
    time.sleep(2)
    
    results['layer_3'] = test_layer_3()
    time.sleep(2)
    
    results['layer_4'] = test_layer_4()
    time.sleep(2)
    
    results['layer_5'] = test_layer_5()
    time.sleep(2)
    
    results['layer_6'] = test_layer_6()
    time.sleep(2)
    
    # Test comprehensive
    results['comprehensive'] = test_comprehensive()
    
    # Summary
    print(f"\n{'='*80}")
    print("📋 TEST SUMMARY")
    print(f"{'='*80}")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
