#!/usr/bin/env python3
"""
Test Groq Classification Fallback
Tests the fallback mechanism when classification confidence is low
"""

import sys
import json
import os

# Add backend to path
sys.path.insert(0, '/workspace/backend')

from services.groq_classification_fallback import get_groq_fallback

def test_fallback_activation():
    """Test that fallback activates for low confidence scores"""
    print("\n🧪 TEST 1: Fallback Activation Threshold")
    print("=" * 60)
    
    fallback = get_groq_fallback()
    
    test_cases = [
        (0.95, False, "High confidence - NO fallback needed"),
        (0.75, False, "Medium-high confidence - NO fallback needed"),
        (0.60, False, "Right at threshold - NO fallback needed"),
        (0.59, True, "Just below threshold - FALLBACK activated"),
        (0.50, True, "Low confidence - FALLBACK activated"),
        (0.25, True, "Very low confidence - FALLBACK activated"),
    ]
    
    for conf, expected, description in test_cases:
        result = fallback.should_use_fallback(conf)
        status = "✅" if result == expected else "❌"
        print(f"{status} {description}")
        print(f"   Confidence: {conf:.2%}, Fallback activated: {result}")
        if result != expected:
            print(f"   ERROR: Expected {expected}, got {result}")
    
    print("\n✅ Threshold testing complete")

def test_fallback_classification():
    """Test actual Groq fallback classification"""
    print("\n🧪 TEST 2: Groq Fallback Classification")
    print("=" * 60)
    
    fallback = get_groq_fallback()
    
    if not fallback.available:
        print("⚠️ Groq API not available, skipping actual classification test")
        return
    
    # Test case 1: Low confidence text classification
    print("\n📄 Test Case 1: Low Confidence Text Document")
    print("-" * 60)
    
    content_preview = "The document contains mixed content with unclear structure. Some sections appear to be research notes while others look like formal documentation. The formatting is inconsistent making it difficult to determine the primary purpose."
    
    original_predictions = {
        'vit': {'predicted_class': 'image', 'confidence': 0.45},  # Low confidence
        'bert': {'predicted_class': 'document', 'confidence': 0.52}  # Low confidence
    }
    
    print(f"Original VIT prediction: {original_predictions['vit']['predicted_class']} ({original_predictions['vit']['confidence']:.2%})")
    print(f"Original BERT prediction: {original_predictions['bert']['predicted_class']} ({original_predictions['bert']['confidence']:.2%})")
    print(f"\nContent preview: {content_preview[:100]}...")
    
    result = fallback.classify_with_groq(content_preview, original_predictions)
    
    if result.get('groq_fallback'):
        groq_result = result['groq_fallback']
        print(f"\n✅ Groq Classification Successful")
        print(f"   Classification: {groq_result.get('classification', 'unknown')}")
        print(f"   Confidence: {groq_result.get('confidence', 0):.2%}")
        print(f"   Reasoning: {groq_result.get('reasoning', '')[:200]}...")
        if groq_result.get('indicators'):
            print(f"   Key Indicators: {', '.join(groq_result.get('indicators', [])[:3])}")
    else:
        print(f"❌ Groq classification failed")
        if result.get('error'):
            print(f"   Error: {result['error']}")

def test_enhance_classification():
    """Test the enhance_classification method"""
    print("\n🧪 TEST 3: Enhance Classification Method")
    print("=" * 60)
    
    fallback = get_groq_fallback()
    
    # Create a classification result with low confidence
    classification_result = {
        'status': 'completed',
        'result': 'text',
        'score': 0.45,  # Low confidence
        'category': 'Document',
        'subcategory': 'Unknown',
        'filename': 'analysis_report.pdf',
        'content_preview': 'This is a mixed content document with unclear classification...',
        'bert_result': {'predicted_class': 'document', 'confidence': 0.48}
    }
    
    print("Input Classification:")
    print(f"  Result: {classification_result['result']}")
    print(f"  Confidence: {classification_result['score']:.2%}")
    print(f"  Category: {classification_result['category']}/{classification_result['subcategory']}")
    
    print("\nEnhancing with Groq fallback...")
    
    if fallback.available:
        enhanced = fallback.enhance_classification(classification_result, classification_result['score'])
        
        print("\n✅ Enhanced Classification:")
        print(f"  Fallback Used: {enhanced.get('fallback_used', False)}")
        if enhanced.get('used_fallback_classification'):
            print(f"  Result: {enhanced['result']}")
            print(f"  Confidence: {enhanced['confidence']:.2%}")
            print(f"  Status: Classification improved by Groq")
        else:
            print(f"  Status: Original classification retained")
            
        if enhanced.get('groq_fallback'):
            print(f"  Groq Reasoning: {enhanced['groq_fallback'].get('reasoning', '')[:150]}...")
    else:
        print("⚠️ Groq API not available")

def test_configuration():
    """Test that fallback is properly configured"""
    print("\n🧪 TEST 4: Configuration Check")
    print("=" * 60)
    
    fallback = get_groq_fallback()
    
    print(f"API Key Configured: {'✅ Yes' if fallback.api_key else '❌ No'}")
    print(f"Model: {fallback.model}")
    print(f"Confidence Threshold: {fallback.confidence_threshold:.2%}")
    print(f"Groq Available: {'✅ Yes' if fallback.available else '❌ No'}")
    
    if fallback.available:
        print("\n✅ Groq Classification Fallback is ready to use")
    else:
        print("\n⚠️ Groq Classification Fallback is not available")
        print("   Check that GROQ_API_KEY environment variable is set")

def main():
    print("\n" + "=" * 60)
    print("🧪 GROQ CLASSIFICATION FALLBACK TEST SUITE")
    print("=" * 60)
    
    # Run all tests
    test_configuration()
    test_fallback_activation()
    
    if get_groq_fallback().available:
        test_fallback_classification()
        test_enhance_classification()
    else:
        print("\n⚠️ Skipping live API tests - Groq not configured")
    
    print("\n" + "=" * 60)
    print("✅ TEST SUITE COMPLETE")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    main()
