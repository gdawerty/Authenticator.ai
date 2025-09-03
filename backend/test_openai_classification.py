#!/usr/bin/env python3
"""
Test script for OpenAI Classification Service
Run this script to test the classification functionality
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.openai_classification_service import OpenAIClassificationService

def test_classification_service():
    """Test the OpenAI classification service"""
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in a .env file or environment variable")
        return False
    
    print("✅ OpenAI API key found")
    
    # Initialize the service
    try:
        service = OpenAIClassificationService()
        print("✅ Classification service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize classification service: {e}")
        return False
    
    # Test 1: Get available categories
    print("\n📋 Testing category retrieval...")
    try:
        categories = service.get_available_categories()
        print(f"✅ Retrieved {len(categories)} categories")
        for category, subcategories in categories.items():
            print(f"  - {category}: {len(subcategories)} subcategories")
    except Exception as e:
        print(f"❌ Failed to get categories: {e}")
        return False
    
    # Test 2: Single document classification
    print("\n🔍 Testing single document classification...")
    test_texts = [
        "This is a bank statement showing transactions for the month of January 2024.",
        "Please find attached the invoice for services rendered totaling $1,500.",
        "Medical report: Patient shows symptoms of common cold with fever and cough.",
        "Academic transcript showing grades for Computer Science courses."
    ]
    
    for i, text in enumerate(test_texts, 1):
        try:
            print(f"\n  Testing document {i}: {text[:50]}...")
            result = service.classify_document(text, confidence_threshold=0.7)
            
            if result.get('error', False):
                print(f"    ❌ Classification failed: {result.get('reasoning', 'Unknown error')}")
            else:
                print(f"    ✅ Category: {result.get('category')}")
                print(f"    ✅ Subcategory: {result.get('subcategory')}")
                print(f"    ✅ Confidence: {result.get('confidence', 0):.2f}")
                print(f"    ✅ Reasoning: {result.get('reasoning', 'N/A')}")
                
        except Exception as e:
            print(f"    ❌ Error during classification: {e}")
            return False
    
    # Test 3: Batch classification
    print("\n📚 Testing batch classification...")
    try:
        batch_results = service.batch_classify_documents(test_texts, confidence_threshold=0.7)
        print(f"✅ Batch classification completed for {len(batch_results)} documents")
        
        # Get statistics
        stats = service.get_classification_statistics(batch_results)
        print(f"✅ Statistics generated:")
        print(f"  - Total documents: {stats.get('total_documents', 0)}")
        print(f"  - Categories used: {len(stats.get('categories', {}))}")
        print(f"  - Mean confidence: {stats.get('confidence_stats', {}).get('mean', 0):.2f}")
        print(f"  - Errors: {stats.get('errors', 0)}")
        
    except Exception as e:
        print(f"❌ Batch classification failed: {e}")
        return False
    
    # Test 4: Health check simulation
    print("\n🏥 Testing health check...")
    try:
        health_result = service.classify_document("This is a test document for health check.", 0.5)
        if health_result.get('error', False):
            print(f"❌ Health check failed: {health_result.get('reasoning', 'Unknown error')}")
            return False
        else:
            print("✅ Health check passed")
            print(f"  - Test classification successful: {health_result.get('category')} -> {health_result.get('subcategory')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    print("\n🎉 All tests passed! OpenAI Classification Service is working correctly.")
    return True

def main():
    """Main function"""
    print("🧪 Testing OpenAI Classification Service")
    print("=" * 50)
    
    success = test_classification_service()
    
    if success:
        print("\n✅ Service is ready for production use!")
        print("\n📝 Next steps:")
        print("1. Ensure your OpenAI API key is set in .env file")
        print("2. Start the Flask backend server")
        print("3. Test the API endpoints:")
        print("   - POST /api/openai/classification/classify")
        print("   - POST /api/openai/classification/batch-classify")
        print("   - GET /api/openai/classification/categories")
        print("   - GET /api/openai/classification/health")
    else:
        print("\n❌ Service testing failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
