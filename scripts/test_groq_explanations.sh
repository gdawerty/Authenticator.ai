#!/bin/bash

echo "🧪 Testing Groq Explanation Service - All 7 Layers"
echo "=================================================="
echo ""

# Check if backend is running
echo "Checking backend health..."
HEALTH=$(curl -s http://localhost:8001/api/explanations/health)
echo "Backend Response: $HEALTH"
echo ""

# Sample data for each layer
echo "📊 Testing Layer 1: Classification"
echo "-----------------------------------"
curl -X POST http://localhost:8001/api/explanations/layer/1 \
  -H "Content-Type: application/json" \
  -d '{
    "layer_result": {
      "result": "text",
      "confidence": 0.97,
      "filename": "document.pdf",
      "file_type": "PDF",
      "encoding": "UTF-8",
      "size_kb": 245
    }
  }' 2>/dev/null | jq '.'
echo ""

echo "📊 Testing Layer 2: Clone Detection"
echo "-----------------------------------"
curl -X POST http://localhost:8001/api/explanations/layer/2 \
  -H "Content-Type: application/json" \
  -d '{
    "layer_result": {
      "similarity_score": 0.45,
      "plagiarism_percentage": 15.2,
      "matched_documents": 3,
      "high_similarity_sections": 2,
      "status": "low_plagiarism"
    }
  }' 2>/dev/null | jq '.'
echo ""

echo "📊 Testing Layer 3: Cryptographic Verification"
echo "----------------------------------------------"
curl -X POST http://localhost:8001/api/explanations/layer/3 \
  -H "Content-Type: application/json" \
  -d '{
    "layer_result": {
      "hash_verification": "valid",
      "signature_status": "verified",
      "certificate_chain": "trusted",
      "timestamp_valid": true,
      "tampering_detected": false,
      "algorithm": "SHA-256"
    }
  }' 2>/dev/null | jq '.'
echo ""

echo "📊 Testing Layer 4: RAG Context"
echo "-------------------------------"
curl -X POST http://localhost:8001/api/explanations/layer/4 \
  -H "Content-Type: application/json" \
  -d '{
    "layer_result": {
      "retrieval_score": 0.92,
      "source_alignment": 0.88,
      "factual_accuracy": 0.85,
      "context_match": true,
      "relevant_documents_found": 5,
      "confidence_level": "high"
    }
  }' 2>/dev/null | jq '.'
echo ""

echo "📊 Testing Layer 5: Authenticity Scoring"
echo "----------------------------------------"
curl -X POST http://localhost:8001/api/explanations/layer/5 \
  -H "Content-Type: application/json" \
  -d '{
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
  }' 2>/dev/null | jq '.'
echo ""

echo "📊 Testing Layer 6: AI Detection"
echo "-------------------------------"
curl -X POST http://localhost:8001/api/explanations/layer/6 \
  -H "Content-Type: application/json" \
  -d '{
    "layer_result": {
      "ai_probability": 0.08,
      "writing_style": "human",
      "pattern_detection": "natural_language",
      "entropy_score": 0.72,
      "ai_generated": false,
      "confidence": 0.91
    }
  }' 2>/dev/null | jq '.'
echo ""

echo "🎯 Testing Comprehensive Explanation"
echo "------------------------------------"
curl -X POST http://localhost:8001/api/explanations/comprehensive \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_result": {
      "filename": "research_paper.pdf",
      "final_score": 87.5,
      "classification": "Authentic",
      "layers_completed": 6,
      "overall_confidence": 0.89,
      "timestamp": "2025-10-26T10:30:00Z"
    }
  }' 2>/dev/null | jq '.'
echo ""

echo "✅ Test Complete!"
echo "=================================================="
