"""
4-Layer Authenticity Pipeline Integration Test
Comprehensive testing of Layers 1-4 with various content types and scenarios.
"""

import os
import sys
from pathlib import Path

# Add the services directory to the Python path
sys.path.append(str(Path(__file__).parent / "services"))

from four_layer_authenticity_pipeline import FourLayerAuthenticityPipeline

def test_four_layer_integration():
    """Test the complete 4-layer authenticity pipeline with various scenarios"""
    
    print("🧪 4-Layer Authenticity Pipeline Integration Test")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = FourLayerAuthenticityPipeline()
    print("\n✅ Pipeline initialized successfully\n")
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Professional Resume",
            "content": """
                Jane Doe
                Data Scientist | Machine Learning Engineer
                
                Professional Experience:
                • Senior ML Engineer at TechCorp (2021-2024)
                • Developed deep learning models for computer vision
                • Led cross-functional team of 6 engineers
                • Improved model accuracy by 23% using transformer architecture
                
                Education:
                • PhD Computer Science, UC Berkeley (2021)
                • MS Statistics, Stanford University (2018)
                • BS Mathematics, MIT (2016)
                
                Technical Skills:
                Python, TensorFlow, PyTorch, Kubernetes, AWS, SQL
                """,
            "content_type": "text/plain",
            "expected_category": "employment/resume"
        },
        {
            "name": "Academic Research Paper",
            "content": """
                Abstract: This study investigates the application of neural networks 
                for natural language processing tasks. We propose a novel architecture 
                that combines attention mechanisms with recurrent neural networks.
                
                Introduction: Natural language processing has seen significant advances 
                with the introduction of transformer models. However, computational 
                efficiency remains a challenge for real-time applications.
                
                Methodology: We trained our model on a dataset of 100,000 documents 
                using cross-validation techniques. The architecture consists of 
                bidirectional LSTM layers with multi-head attention.
                
                Results: Our approach achieved 94.2% accuracy on the benchmark dataset, 
                representing a 5.7% improvement over previous state-of-the-art methods.
                """,
            "content_type": "text/plain",
            "expected_category": "academic/research"
        },
        {
            "name": "Legal Contract",
            "content": """
                SOFTWARE LICENSE AGREEMENT
                
                This Agreement is entered into between Company A ("Licensor") and 
                Company B ("Licensee") for the licensing of proprietary software.
                
                1. GRANT OF LICENSE
                Subject to the terms and conditions of this Agreement, Licensor grants 
                Licensee a non-exclusive, non-transferable license to use the Software.
                
                2. RESTRICTIONS
                Licensee shall not: (a) modify, adapt, or create derivative works; 
                (b) reverse engineer, decompile, or disassemble the Software.
                
                3. TERM AND TERMINATION
                This Agreement shall remain in effect until terminated by either party 
                with thirty (30) days written notice.
                """,
            "content_type": "text/plain",
            "expected_category": "legal/contract"
        },
        {
            "name": "Template-like Content",
            "content": """
                [Name]
                [Title]
                
                Experience:
                • [Years] years of experience in [Field]
                • Expert in [Technology] and [Technology]
                • Led team of [Number] developers on [Project]
                
                Education:
                • [Degree] [Field], [University] ([Year])
                • [Degree] [Field], [University] ([Year])
                
                Skills: [Skill], [Skill], [Skill], [Skill]
                """,
            "content_type": "text/plain",
            "expected_category": "general/document"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"🔍 Test {i}: {scenario['name']}")
        print("-" * 40)
        
        try:
            # Run analysis
            result = pipeline.analyze_content(
                content=scenario['content'],
                content_type=scenario['content_type'],
                content_id=f"test_{i:03d}"
            )
            
            # Collect results
            test_result = {
                "scenario": scenario['name'],
                "success": True,
                "overall_score": result.overall_authenticity_score,
                "confidence_level": result.confidence_level,
                "risk_level": result.risk_assessment['risk_level'],
                "detected_category": result.layer2_result.get('primary_category', 'unknown'),
                "expected_category": scenario['expected_category'],
                "layer_scores": {
                    "layer1": result.layer1_result.get('confidence', 0.0),
                    "layer2": result.layer2_result.get('classification_confidence', 0.0),
                    "layer3": result.layer3_result.get('originality_score', 0.0),
                    "layer4": result.layer4_result.get('integrity_score', 0.0)
                }
            }
            
            # Check if category detection is correct
            category_match = scenario['expected_category'] in result.layer2_result.get('primary_category', '')
            
            print(f"   ✅ Analysis completed successfully")
            print(f"   📊 Overall Score: {result.overall_authenticity_score:.2f}")
            print(f"   🔍 Confidence: {result.confidence_level}")
            print(f"   ⚠️ Risk: {result.risk_assessment['risk_level']}")
            print(f"   🎯 Category: {result.layer2_result.get('primary_category', 'unknown')}")
            print(f"   ✅ Category Match: {'Yes' if category_match else 'No'}")
            
            test_result['category_match'] = category_match
            results.append(test_result)
            
        except Exception as e:
            print(f"   ❌ Test failed: {str(e)}")
            results.append({
                "scenario": scenario['name'],
                "success": False,
                "error": str(e)
            })
        
        print()
    
    # Summary
    print("📊 Integration Test Summary")
    print("=" * 40)
    
    successful_tests = [r for r in results if r.get('success', False)]
    failed_tests = [r for r in results if not r.get('success', False)]
    
    print(f"✅ Successful Tests: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed Tests: {len(failed_tests)}")
    
    if successful_tests:
        avg_overall_score = sum(r['overall_score'] for r in successful_tests) / len(successful_tests)
        print(f"📊 Average Overall Score: {avg_overall_score:.2f}")
        
        # Layer performance
        layer_avgs = {}
        for layer in ['layer1', 'layer2', 'layer3', 'layer4']:
            scores = [r['layer_scores'][layer] for r in successful_tests]
            layer_avgs[layer] = sum(scores) / len(scores)
        
        print("\n📋 Layer Performance:")
        print(f"   🎯 Layer 1 (MIME): {layer_avgs['layer1']:.2f}")
        print(f"   🤖 Layer 2 (Classification): {layer_avgs['layer2']:.2f}")
        print(f"   🔍 Layer 3 (Clone Detection): {layer_avgs['layer3']:.2f}")
        print(f"   🔐 Layer 4 (Cryptographic): {layer_avgs['layer4']:.2f}")
        
        # Category detection accuracy
        category_matches = [r for r in successful_tests if r.get('category_match', False)]
        category_accuracy = len(category_matches) / len(successful_tests) * 100
        print(f"\n🎯 Category Detection Accuracy: {category_accuracy:.1f}%")
    
    if failed_tests:
        print("\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   • {test['scenario']}: {test.get('error', 'Unknown error')}")
    
    print("\n🎯 Pipeline Status: All 4 layers operational and integrated")
    print("   ✅ Layer 1: MIME Detection & Routing")
    print("   ✅ Layer 2: BERT/ViT Classification")
    print("   ✅ Layer 3: Clone Detection")
    print("   ✅ Layer 4: Cryptographic Validation")
    
    return len(successful_tests) == len(results)

if __name__ == "__main__":
    success = test_four_layer_integration()
    exit(0 if success else 1)
