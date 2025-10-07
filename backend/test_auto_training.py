"""
Auto-Training Demo for Enhanced Stage 3 Clone Detection
Shows how the system automatically learns from every document processed
"""

def demo_auto_training():
    print("🤖 Auto-Training Clone Detection Demo")
    print("=" * 50)
    
    from services.enhanced_clone_detection_service import enhanced_clone_detection_service
    
    # Start with clean slate
    enhanced_clone_detection_service.update_similarity_threshold(0.80)
    
    print("📊 Initial system state:")
    initial_stats = enhanced_clone_detection_service.get_statistics()
    print(f"  Documents in training set: {initial_stats['total_fingerprints']}")
    print(f"  Training quality: {enhanced_clone_detection_service.get_training_quality_metrics()['training_data_quality']}")
    
    # Simulate a sequence of document submissions
    documents = [
        {
            'id': 'contract_001',
            'filename': 'employment_contract_template.txt',
            'text': '''EMPLOYMENT AGREEMENT
            
This Employment Agreement is entered into between TechCorp Inc. and [Employee Name].

Position: Software Engineer
Department: Engineering
Start Date: [Start Date]
Salary: $[Amount] per year
Benefits: Health insurance, 401k, vacation days

The employee agrees to:
1. Perform duties diligently
2. Maintain confidentiality
3. Follow company policies

This agreement is governed by the laws of [State].''',
            'type': 'employment_contract'
        },
        {
            'id': 'contract_002', 
            'filename': 'similar_employment_contract.txt',
            'text': '''EMPLOYMENT AGREEMENT
            
This Employment Agreement is entered into between TechCorp Inc. and John Smith.

Position: Software Engineer  
Department: Engineering
Start Date: January 15, 2024
Salary: $85,000 per year
Benefits: Health insurance, 401k, vacation days

The employee agrees to:
1. Perform duties diligently
2. Maintain confidentiality  
3. Follow company policies

This agreement is governed by the laws of California.''',
            'type': 'employment_contract'
        },
        {
            'id': 'report_001',
            'filename': 'quarterly_report.txt', 
            'text': '''QUARTERLY BUSINESS REPORT - Q3 2024

Executive Summary:
This quarter showed strong performance across all key metrics.

Financial Highlights:
- Revenue: $2.5M (up 15% from Q2)
- Expenses: $1.8M
- Net Profit: $700K

Key Achievements:
- Launched new product line
- Expanded team by 20%
- Improved customer satisfaction scores

Challenges:
- Supply chain delays
- Increased competition
- Market volatility

Outlook for Q4:
We expect continued growth with focus on operational efficiency.''',
            'type': 'business_report'
        },
        {
            'id': 'contract_003',
            'filename': 'consultant_agreement.txt',
            'text': '''CONSULTING AGREEMENT

This Consulting Agreement is between TechCorp Inc. and [Consultant Name].

Services: Technical consulting and software architecture
Duration: 6 months
Rate: $150 per hour
Payment Terms: Net 30

The consultant agrees to:
1. Provide expert technical guidance
2. Deliver high-quality work products
3. Meet agreed-upon deadlines

Confidentiality and intellectual property terms apply.''',
            'type': 'consulting_contract'
        },
        {
            'id': 'contract_004',
            'filename': 'modified_employment_contract.txt',
            'text': '''EMPLOYMENT AGREEMENT

This Employment Agreement is entered into between TechCorp Inc. and Jane Doe.

Position: Senior Software Engineer
Department: Engineering  
Start Date: February 1, 2024
Salary: $95,000 per year
Benefits: Health insurance, 401k, vacation days, stock options

The employee agrees to:
1. Perform duties diligently
2. Maintain confidentiality
3. Follow company policies
4. Participate in on-call rotation

This agreement is governed by the laws of California.

Additional clauses:
- Remote work allowed 2 days per week
- Annual performance review required''',
            'type': 'employment_contract'
        }
    ]
    
    print(f"\n🔄 Processing {len(documents)} documents with auto-training...")
    results = []
    
    for i, doc in enumerate(documents, 1):
        print(f"\n--- Document {i}: {doc['filename']} ---")
        
        # Process with auto-training enabled
        result = enhanced_clone_detection_service.process_document(
            text=doc['text'],
            file_id=doc['id'],
            filename=doc['filename'],
            document_type=doc['type'],
            auto_train=True
        )
        
        results.append(result)
        
        # Show immediate results
        print(f"Similarity Score: {result['similarity_score']:.3f}")
        print(f"Training Status: {'✅ TRAINED' if result['training_status']['trained'] else '❌ NOT TRAINED'}")
        if not result['training_status']['trained']:
            print(f"Reason: {result['training_status']['reason']}")
        
        if result['similarity_matches']:
            print(f"Similar Documents Found: {len(result['similarity_matches'])}")
            for match in result['similarity_matches'][:2]:
                print(f"  - {match['filename']}: {match['similarity_score']:.3f}")
        else:
            print("No similar documents found")
    
    print(f"\n📊 Final system state after auto-training:")
    final_stats = enhanced_clone_detection_service.get_statistics()
    training_quality = enhanced_clone_detection_service.get_training_quality_metrics()
    
    print(f"  Documents in training set: {final_stats['total_fingerprints']}")
    print(f"  Total similarity matches: {final_stats['total_similarity_matches']}")
    print(f"  Training events: {final_stats['training_statistics']['total_training_events']}")
    print(f"  Recent training events: {final_stats['training_statistics']['recent_training_events']}")
    print(f"  Training data quality: {training_quality['training_data_quality']}")
    print(f"  Duplicate encounters: {training_quality['duplicate_encounters']}")
    
    print(f"\n📈 Document type distribution:")
    for doc_type, count in final_stats['document_type_distribution'].items():
        print(f"  {doc_type}: {count} documents")
    
    print(f"\n🔍 Clone Detection Analysis:")
    print("=" * 30)
    
    # Analyze the clone detection patterns
    clone_patterns = analyze_clone_patterns(results)
    for pattern_type, details in clone_patterns.items():
        print(f"{pattern_type}: {details}")
    
    print(f"\n✅ Auto-Training Demo Complete!")
    print("The system has automatically learned from all processed documents.")
    print("Future documents will be compared against this growing knowledge base!")

def analyze_clone_patterns(results):
    """Analyze clone detection patterns from the results"""
    patterns = {
        'High Similarity Contracts': 0,
        'Unique Documents': 0,
        'Template Variations': 0,
        'Cross-Type Similarities': 0
    }
    
    for result in results:
        similarity = result['similarity_score']
        doc_type = result['metadata']['document_type']
        matches = result['similarity_matches']
        
        if similarity > 0.85:
            patterns['High Similarity Contracts'] += 1
        elif similarity == 0.0:
            patterns['Unique Documents'] += 1
        elif 0.0 < similarity <= 0.85:
            patterns['Template Variations'] += 1
            
        # Check for cross-type similarities
        for match in matches:
            # This would require storing doc types in matches
            # For demo, we'll simulate
            if 'contract' in result['filename'] and 'report' in match.get('filename', ''):
                patterns['Cross-Type Similarities'] += 1
    
    return patterns

def test_training_management():
    """Test training management features"""
    print(f"\n🛠️  Testing Training Management Features")
    print("-" * 40)
    
    from services.enhanced_clone_detection_service import enhanced_clone_detection_service
    
    # Test manual training
    print("1. Manual Training Test:")
    manual_result = enhanced_clone_detection_service.process_document(
        text="This is a manually added test document for training purposes.",
        file_id="manual_test_001",
        filename="manual_test.txt",
        document_type="test",
        auto_train=True
    )
    print(f"   Manual training successful: {manual_result['training_status']['trained']}")
    
    # Test analysis without training
    print("\n2. Analysis Without Training Test:")
    no_train_result = enhanced_clone_detection_service.process_document(
        text="This document will be analyzed but not added to training set.",
        file_id="no_train_001", 
        filename="temp_analysis.txt",
        document_type="temporary",
        auto_train=False
    )
    print(f"   Document analyzed: {no_train_result['similarity_score']:.3f}")
    print(f"   Training skipped: {not no_train_result['training_status']['trained']}")
    
    # Test removal from training
    print("\n3. Remove from Training Test:")
    removal_result = enhanced_clone_detection_service.remove_document_from_training("manual_test_001")
    print(f"   Removal successful: {removal_result['success']}")
    
    print("\n✅ Training Management Tests Complete!")

if __name__ == "__main__":
    demo_auto_training()
    test_training_management()
