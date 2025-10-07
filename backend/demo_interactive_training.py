"""
Interactive Demo with User Training Prompts
Shows how the system prompts users to train on documents after analysis
"""

def interactive_demo():
    print("🎯 Interactive Clone Detection Demo with Training Prompts")
    print("=" * 60)
    
    from services.enhanced_clone_detection_service import enhanced_clone_detection_service
    
    # Set up the service
    enhanced_clone_detection_service.update_similarity_threshold(0.80)
    
    # Sample documents for interactive demo
    test_documents = [
        {
            'filename': 'employment_contract_v1.txt',
            'text': '''EMPLOYMENT CONTRACT

This Employment Agreement is entered into between TechCorp Inc. and Alice Johnson.

Position: Senior Software Engineer
Department: Engineering
Start Date: March 1, 2024
Salary: $90,000 per year
Benefits: Health, dental, vision insurance, 401k matching, 15 vacation days

The employee agrees to:
1. Perform assigned duties with diligence and care
2. Maintain strict confidentiality of proprietary information
3. Follow all company policies and procedures
4. Participate in on-call rotation as needed

This agreement is governed by California state law.''',
            'type': 'employment_contract'
        },
        {
            'filename': 'similar_contract_v2.txt', 
            'text': '''EMPLOYMENT CONTRACT

This Employment Agreement is entered into between TechCorp Inc. and Bob Smith.

Position: Software Engineer
Department: Engineering  
Start Date: March 15, 2024
Salary: $85,000 per year
Benefits: Health, dental, vision insurance, 401k matching, 12 vacation days

The employee agrees to:
1. Perform assigned duties with diligence and care
2. Maintain strict confidentiality of proprietary information
3. Follow all company policies and procedures

This agreement is governed by California state law.''',
            'type': 'employment_contract'
        },
        {
            'filename': 'project_proposal.txt',
            'text': '''PROJECT PROPOSAL: AI-Powered Customer Support

Objective: Implement an AI chatbot system to handle customer inquiries.

Scope:
- Natural language processing for customer queries
- Integration with existing support ticketing system
- 24/7 automated response capability
- Escalation to human agents when needed

Timeline: 4 months
Budget: $150,000
Team: 3 engineers, 1 PM, 1 designer

Expected Benefits:
- 40% reduction in support response time
- 60% of queries handled automatically
- Improved customer satisfaction scores
- Cost savings of $200K annually

Risk Assessment:
- Technical complexity: Medium
- Resource availability: High
- Customer acceptance: Medium''',
            'type': 'project_proposal'
        }
    ]
    
    print(f"\\n📋 We'll analyze {len(test_documents)} documents and prompt for training decisions...")
    
    for i, doc in enumerate(test_documents, 1):
        print(f"\\n{'='*50}")
        print(f"📄 Document {i}: {doc['filename']}")
        print(f"📝 Content preview: {doc['text'][:100]}...")
        print(f"📂 Type: {doc['type']}")
        
        # Analyze without training first (simulate the prompt mode)
        print(f"\n🔍 Analyzing document for clones...")
        
        result = enhanced_clone_detection_service.process_document(
            text=doc['text'],
            file_id=f'demo_{i}_{doc["filename"]}',
            filename=doc['filename'],
            document_type=doc['type'],
            auto_train=False  # Don't train yet
        )
        
        # Show analysis results
        print(f"\\n📊 Analysis Results:")
        print(f"   Similarity Score: {result['similarity_score']:.3f}")
        print(f"   Similar Documents: {len(result['similarity_matches'])}")
        
        if result['similarity_matches']:
            print(f"   🔗 Best Match: {result['similarity_matches'][0]['filename']}")
            print(f"      Match Score: {result['similarity_matches'][0]['similarity_score']:.3f}")
        
        # Generate training recommendation
        training_rec = generate_training_recommendation(result, doc['text'])
        
        print(f"\n🤖 Training Recommendation:")
        print(f"   Should Train: {'✅ YES' if training_rec['should_train'] else '❌ NO'}")
        print(f"   Confidence: {training_rec['confidence'].upper()}")
        
        if training_rec['reasons']:
            print(f"   📝 Reasons:")
            for reason in training_rec['reasons']:
                print(f"      - {reason}")
        
        if training_rec['benefits']:
            print(f"   ✅ Benefits:")
            for benefit in training_rec['benefits']:
                print(f"      - {benefit}")
                
        if training_rec['concerns']:
            print(f"   ⚠️  Concerns:")
            for concern in training_rec['concerns']:
                print(f"      - {concern}")
        
        # Interactive prompt
        print(f"\n❓ Training Decision:")
        user_choice = get_user_training_decision(doc['filename'], training_rec)
        
        if user_choice:
            print(f"\n✅ User chose to TRAIN on this document")
            
            # Now train on the document
            training_result = enhanced_clone_detection_service.process_document(
                text=doc['text'],
                file_id=f'demo_{i}_{doc["filename"]}',
                filename=doc['filename'],
                document_type=doc['type'],
                auto_train=True
            )
            
            if training_result['training_status']['trained']:
                print(f"   🎯 Training successful!")
                print(f"   📝 Reason: {training_result['training_status']['reason']}")
            else:
                print(f"   ❌ Training failed")
                print(f"   📝 Reason: {training_result['training_status']['reason']}")
        else:
            print(f"\n❌ User chose NOT to train on this document")
            print(f"   📝 Document analyzed but not added to knowledge base")
        
        print(f"\n⏱️  Processing completed in {result['metadata']['processing_time_ms']:.1f}ms")
    
    # Final statistics
    print(f"\\n{'='*50}")
    print(f"📊 Final Training Statistics:")
    final_stats = enhanced_clone_detection_service.get_statistics()
    print(f"   Total documents in training: {final_stats['total_fingerprints']}")
    print(f"   Training events today: {final_stats['training_statistics']['recent_training_events']}")
    print(f"   Training quality: {enhanced_clone_detection_service.get_training_quality_metrics()['training_data_quality']}")
    
    print(f"\\n✅ Interactive Demo Complete!")
    print(f"Users now have full control over what gets trained! 🎮")

def generate_training_recommendation(analysis_result: dict, text_content: str) -> dict:
    """Generate training recommendation based on analysis results"""
    recommendation = {
        'should_train': False,
        'confidence': 'low',
        'reasons': [],
        'benefits': [],
        'concerns': []
    }
    
    similarity_score = analysis_result.get('similarity_score', 0.0)
    matches = analysis_result.get('similarity_matches', [])
    text_length = len(text_content)
    
    # Analyze if training would be beneficial
    if similarity_score < 0.95:  # Not a near-duplicate
        recommendation['should_train'] = True
        recommendation['reasons'].append('Document is unique enough to add value to training set')
        
        if text_length > 500:
            recommendation['confidence'] = 'high'
            recommendation['benefits'].append('Excellent content length for meaningful fingerprints')
        elif text_length > 200:
            recommendation['confidence'] = 'medium'
            recommendation['benefits'].append('Good content length for training')
        elif text_length > 50:
            recommendation['confidence'] = 'low'
            recommendation['benefits'].append('Adequate content for basic training')
        else:
            recommendation['confidence'] = 'very_low'
            recommendation['concerns'].append('Document might be too short for effective training')
        
        if len(matches) == 0:
            recommendation['benefits'].append('No similar documents found - adds completely new knowledge')
        elif len(matches) > 0 and similarity_score < 0.85:
            recommendation['benefits'].append('Moderate similarity - helps refine detection boundaries')
        elif len(matches) > 0 and similarity_score >= 0.85:
            recommendation['concerns'].append('High similarity - may provide limited additional value')
            
    else:
        recommendation['should_train'] = False
        recommendation['reasons'].append(f'Document too similar to existing ({similarity_score:.1%})')
        recommendation['concerns'].append('Training on near-duplicates can reduce detection accuracy')
    
    # Additional analysis
    duplicates_found = analysis_result.get('duplicates_found', 0)
    if duplicates_found > 0:
        recommendation['concerns'].append(f'{duplicates_found} near-duplicates detected')
    
    return recommendation

def get_user_training_decision(filename: str, recommendation: dict) -> bool:
    """Simulate user decision making (in real app, this would be UI)"""
    print(f"\\n   Would you like to train the clone detection system on '{filename}'?")
    
    # Auto-decision based on recommendation for demo
    if recommendation['should_train'] and recommendation['confidence'] in ['high', 'medium']:
        print(f"   [Demo: Auto-accepting based on {recommendation['confidence']} confidence recommendation]")
        return True
    elif recommendation['should_train'] and recommendation['confidence'] == 'low':
        print(f"   [Demo: User considering... accepting with low confidence]")
        return True
    else:
        print(f"   [Demo: Auto-declining based on recommendation]")
        return False

def simulate_api_usage():
    """Show how this works through the API"""
    print(f"\\n🌐 API Usage Examples:")
    print("-" * 30)
    
    print(f"1. Analyze with training prompt:")
    print(f"   POST /api/stage3/analyze")
    print(f"   Form data: file=document.pdf, auto_train=prompt")
    print(f"   Response: analysis + training_recommendation")
    
    print(f"\\n2. User confirms training:")
    print(f"   POST /api/stage3/training/confirm")
    print(f"   JSON: {{file_id, text, filename, train: true}}")
    
    print(f"\\n3. Or analyze without training:")
    print(f"   POST /api/stage3/analyze")
    print(f"   Form data: file=document.pdf, auto_train=false")

if __name__ == "__main__":
    interactive_demo()
    simulate_api_usage()
