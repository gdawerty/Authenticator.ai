#!/usr/bin/env python3
"""
Test script for the AI Detection Layer with Fast-DetectGPT
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, '/Users/prathamsaurabh/Authenticator.ai/backend/layers/layer6_ai_detection')

def test_ai_detection():
    """Test the AI detection layer"""
    try:
        from ai_detector import AIDetectionLayer
        
        print("🔄 Initializing AI Detection Layer...")
        detector = AIDetectionLayer()
        
        print(f"✅ Layer initialized: {detector.get_layer_info()}")
        
        # Test with sample text
        sample_texts = [
            # Human-written text (more natural, varied)
            "Hey there! I was just thinking about our conversation yesterday. The weather has been absolutely crazy lately - one day it's sunny, the next it's pouring rain. Makes it really hard to plan outdoor activities, you know?",
            
            # AI-generated text (more formal, structured)  
            "In conclusion, it is important to note that the implementation of artificial intelligence technologies requires careful consideration of various factors. Furthermore, organizations must evaluate the potential benefits and challenges associated with these systems. Therefore, it is essential to develop comprehensive strategies that address both technical and ethical considerations."
        ]
        
        for i, text in enumerate(sample_texts):
            print(f"\n🔍 Testing text {i+1}:")
            print(f"Text: {text[:100]}...")
            
            result = detector.analyze(f"test_{i+1}.txt", text)
            
            print(f"Result: {result['method']}")
            print(f"AI Generated: {result['is_ai_generated']}")
            print(f"AI Probability: {result['ai_probability']:.3f}")
            print(f"Confidence: {result['confidence']:.3f}")
            print(f"Processing Time: {result['processing_time']:.3f}s")
            
            if 'details' in result:
                if result['method'] == 'fast_detect_gpt':
                    print(f"Discrepancy Score: {result['details'].get('discrepancy_score', 'N/A')}")
                    print(f"Model: {result['details'].get('model_config', 'N/A')}")
                elif result['method'] in ['heuristic_fallback', 'heuristic_analysis']:
                    print(f"Pattern Score: {result['details'].get('pattern_score', 'N/A')}")
                    print(f"Vocab Diversity: {result['details'].get('vocabulary_diversity', 'N/A')}")
        
        print("\n✅ AI Detection Layer test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI Detection Layer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing AI Detection Layer with Fast-DetectGPT")
    print("=" * 60)
    
    success = test_ai_detection()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)
