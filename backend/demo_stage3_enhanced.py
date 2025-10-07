"""
Quick Demo: Enhanced Stage 3 Clone Detection in Action
Shows how the SimHash & MinHash implementation works
"""

def demo_stage3_clone_detection():
    print("🚀 Enhanced Stage 3 Clone Detection Demo")
    print("=" * 50)
    
    # Sample documents for testing
    documents = {
        "original_contract.txt": """
        EMPLOYMENT CONTRACT
        This agreement is between Company ABC and John Doe.
        The employee shall perform duties as Software Engineer.
        Salary: $75,000 per year.
        Start Date: January 1, 2024.
        """,
        
        "modified_contract.txt": """
        EMPLOYMENT CONTRACT  
        This agreement is between Company ABC and John Doe.
        The employee shall perform duties as Software Engineer.
        Salary: $75,000 per year.
        Start Date: January 1, 2024.
        Additional clause: Employee agrees to confidentiality terms.
        """,
        
        "different_contract.txt": """
        CONSULTING AGREEMENT
        This contract is between XYZ Corp and Jane Smith.
        The consultant will provide marketing services.
        Rate: $100/hour.
        Project Duration: 6 months.
        """
    }
    
    from services.enhanced_clone_detection_service import enhanced_clone_detection_service
    
    # Set appropriate threshold
    enhanced_clone_detection_service.update_similarity_threshold(0.80)
    
    print("📄 Processing documents through Stage 3...")
    results = {}
    
    for filename, content in documents.items():
        print(f"\nProcessing: {filename}")
        
        result = enhanced_clone_detection_service.process_document(
            text=content.strip(),
            file_id=f"demo_{filename}",
            filename=filename,
            document_type="contract"
        )
        
        results[filename] = result
        
        print(f"  SimHash: {result['fingerprint_data']['simhash'][:16]}...")
        print(f"  Shingles: {result['fingerprint_data']['shingles_count']}")
        print(f"  Max Similarity: {result['similarity_score']:.3f}")
        
        if result['similarity_matches']:
            print(f"  🔍 Similar Documents Found:")
            for match in result['similarity_matches'][:2]:  # Top 2
                print(f"    - {match['filename']}: {match['similarity_score']:.3f} ({match['match_method']})")
    
    print("\n📊 Stage 3 Analysis Summary:")
    print("-" * 30)
    
    for filename, result in results.items():
        risk_level = "HIGH" if result['similarity_score'] > 0.9 else "MEDIUM" if result['similarity_score'] > 0.7 else "LOW"
        print(f"{filename:20} | Similarity: {result['similarity_score']:.3f} | Risk: {risk_level}")
    
    print("\n🎯 Pipeline Integration Example:")
    print("-" * 40)
    
    # Show how this integrates with your pipeline
    pipeline_output = {
        "stage": "stage_3_clone_detection",
        "enhanced_clone_detection": {
            "similarity_score": 0.87,
            "duplicates_found": 2,
            "detection_methods": ["simhash", "minhash"]
        },
        "clone_detection_summary": {
            "max_similarity_score": 0.87,
            "high_similarity_matches": 1,
            "exact_matches": 0
        },
        "duplicate_risk_score": 0.87
    }
    
    print("Sample Pipeline Output:")
    import json
    print(json.dumps(pipeline_output, indent=2))
    
    print("\n✅ Stage 3 Enhanced Clone Detection Demo Complete!")

if __name__ == "__main__":
    demo_stage3_clone_detection()
