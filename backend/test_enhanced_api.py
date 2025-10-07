"""
Test the enhanced /analyze endpoint with training prompts
"""

import requests
import json

def test_analyze_with_prompt():
    """Test the /analyze endpoint with auto_train=prompt"""
    
    print("🧪 Testing Enhanced /analyze Endpoint with Training Prompts")
    print("=" * 60)
    
    # Test document
    test_text = """EMPLOYMENT CONTRACT

This Employment Agreement is between ABC Corp and Jane Smith.

Position: Data Scientist
Department: Analytics
Start Date: April 1, 2024
Salary: $95,000 per year

The employee agrees to maintain confidentiality and follow company policies."""
    
    # Create a temporary file for testing
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_text)
        temp_file_path = f.name
    
    try:
        print("📄 Test Document:")
        print(f"   Content: {test_text[:100]}...")
        print(f"   Length: {len(test_text)} characters")
        
        # Test 1: Analyze with prompt mode
        print(f"\n🔍 Test 1: Analyze with training prompt")
        
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_contract.txt', f, 'text/plain')}
            data = {
                'auto_train': 'prompt',
                'similarity_threshold': 0.80,
                'document_type': 'employment_contract'
            }
            
            response = requests.post(
                'http://localhost:5000/api/stage3/analyze',
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis successful!")
            print(f"   Similarity Score: {result.get('similarity_score', 0):.3f}")
            print(f"   Training Status: {result.get('training_status', {}).get('trained', 'N/A')}")
            
            # Check for training recommendation
            if 'training_recommendation' in result:
                rec = result['training_recommendation']
                print(f"\n🤖 Training Recommendation:")
                print(f"   Should Train: {'✅ YES' if rec['should_train'] else '❌ NO'}")
                print(f"   Confidence: {rec['confidence']}")
                
                if rec.get('benefits'):
                    print(f"   Benefits: {', '.join(rec['benefits'][:2])}")
                
                # Test 2: Confirm training based on recommendation
                if rec['should_train']:
                    print(f"\n✅ Test 2: User accepts training recommendation")
                    
                    confirm_data = {
                        'file_id': result['file_id'],
                        'text': test_text,
                        'filename': 'test_contract.txt',
                        'document_type': 'employment_contract',
                        'train': True
                    }
                    
                    confirm_response = requests.post(
                        'http://localhost:5000/api/stage3/training/confirm',
                        json=confirm_data
                    )
                    
                    if confirm_response.status_code == 200:
                        confirm_result = confirm_response.json()
                        print(f"   Training confirmed: {confirm_result['message']}")
                        print(f"   Status: {confirm_result['training_status']['trained']}")
                    else:
                        print(f"   ❌ Training confirmation failed: {confirm_response.text}")
                else:
                    print(f"\n❌ Test 2: Recommendation is not to train")
            else:
                print(f"   ⚠️  No training recommendation found in response")
        else:
            print(f"❌ Analysis failed: {response.status_code} - {response.text}")
        
        # Test 3: Analyze without training
        print(f"\n🔍 Test 3: Analyze without training (auto_train=false)")
        
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_no_train.txt', f, 'text/plain')}
            data = {
                'auto_train': 'false',
                'similarity_threshold': 0.80,
                'document_type': 'test'
            }
            
            response = requests.post(
                'http://localhost:5000/api/stage3/analyze',
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis without training successful!")
            print(f"   Similarity Score: {result.get('similarity_score', 0):.3f}")
            print(f"   Training Status: {result.get('training_status', {}).get('trained', 'N/A')}")
            print(f"   Pipeline Stage: {result.get('pipeline_stage', 'N/A')}")
        else:
            print(f"❌ Analysis failed: {response.status_code} - {response.text}")
        
        # Test 4: Get system statistics
        print(f"\n📊 Test 4: System Statistics")
        
        stats_response = requests.get('http://localhost:5000/api/stage3/statistics')
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"✅ Statistics retrieved:")
            print(f"   Total fingerprints: {stats.get('total_fingerprints', 0)}")
            print(f"   Training events: {stats.get('training_statistics', {}).get('total_training_events', 0)}")
            print(f"   Training quality: {stats.get('training_statistics', {}).get('training_data_quality', 'N/A')}")
        else:
            print(f"❌ Statistics failed: {stats_response.status_code}")
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass
    
    print(f"\n✅ Enhanced API Testing Complete!")

def show_api_flow():
    """Show the complete API flow"""
    print(f"\n📋 Complete API Flow with Training Prompts:")
    print("-" * 50)
    print(f"1. 📤 User uploads document")
    print(f"   POST /api/stage3/analyze (auto_train=prompt)")
    print(f"   ↓")
    print(f"2. 🔍 System analyzes for clones")
    print(f"   Returns: similarity_score + training_recommendation")
    print(f"   ↓")
    print(f"3. 🤖 AI recommends training action")
    print(f"   Factors: similarity, content quality, benefits vs concerns")
    print(f"   ↓")
    print(f"4. 👤 User decides")
    print(f"   Accept: POST /api/stage3/training/confirm (train=true)")
    print(f"   Decline: No further action needed")
    print(f"   ↓")
    print(f"5. 🧠 System learns (if accepted)")
    print(f"   Document added to knowledge base for future detection")

if __name__ == "__main__":
    test_analyze_with_prompt()
    show_api_flow()
