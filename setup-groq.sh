#!/bin/bash

# 🚀 Groq Cloud Integration Setup Script
# Sets up Groq API key and verifies connection

set -e

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║        🚀 GROQ CLOUD INTEGRATION SETUP                           ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env file exists
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env file from template..."
    cp backend/env_template.txt backend/.env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  Please edit backend/.env and add your Groq API key"
    echo "   Get your free API key at: https://console.groq.com/keys"
    echo ""
    exit 1
fi

# Check if GROQ_API_KEY is set
if grep -q "GROQ_API_KEY=gsk_" backend/.env; then
    echo "✅ Groq API key found in backend/.env"
    
    # Extract API key
    GROQ_API_KEY=$(grep "GROQ_API_KEY=" backend/.env | cut -d'=' -f2 | sed 's/gsk_/gsk_.../')
    echo "   API Key: $GROQ_API_KEY...u9qO"
else
    echo "⚠️  No valid Groq API key found in backend/.env"
    echo ""
    echo "📝 Steps to get your Groq API key:"
    echo "   1. Visit: https://console.groq.com"
    echo "   2. Sign up for a free account (no credit card needed)"
    echo "   3. Go to: https://console.groq.com/keys"
    echo "   4. Create a new API key"
    echo "   5. Copy the key (starts with 'gsk_')"
    echo "   6. Add to backend/.env: GROQ_API_KEY=gsk_your_key_here"
    echo ""
    exit 1
fi

echo ""
echo "🧪 Testing Groq API Connection..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test with Python
cd backend

python3 << 'EOF'
import os
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from services.groq_explanation_service import get_groq_service

print("🔍 Checking Groq service configuration...")
groq_service = get_groq_service()

if groq_service.available:
    print("✅ Groq API Key: Configured")
    print(f"✅ Model: {groq_service.model}")
    print("✅ Service Status: Ready")
    print("")
    print("🧪 Testing Layer Explanation Generation...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")
    
    # Test Layer 1
    test_layer_1 = {
        'result': 'text',
        'confidence': 0.97,
        'filename': 'test_document.pdf'
    }
    
    print("Testing Layer 1 - Classification...")
    explanation_1 = groq_service.generate_layer_1_explanation(test_layer_1)
    print(f"✅ Result: {explanation_1[:100]}...")
    print("")
    
    print("✅ Groq Cloud Integration is Ready!")
    print("")
    print("📚 Next Steps:")
    print("   1. Rebuild Docker containers: docker-compose down && docker-compose up --build")
    print("   2. Access explanation endpoints: POST /api/explanations/*")
    print("   3. Frontend integration ready!")
else:
    print("❌ Groq API Key: NOT Configured")
    print("⚠️  Explanations will be disabled")
    sys.exit(1)
EOF

cd ..

echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║        ✅ GROQ SETUP COMPLETE                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo "📖 Documentation: GROQ_INTEGRATION_GUIDE.md"
echo "🚀 Ready to use Groq Cloud for layer explanations!"
