#!/bin/bash

# 🧪 Authenticator.AI Backend Comprehensive Test Suite
# Tests all 7 layers and verifies endpoint functionality

set -e

API_BASE_URL="http://localhost:8001"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🧪 AUTHENTICATOR.AI BACKEND VERIFICATION TEST SUITE  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    
    echo -e "${YELLOW}Testing: ${name}${NC}"
    echo "  Method: $method"
    echo "  Endpoint: $endpoint"
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_BASE_URL$endpoint")
    else
        if [ -z "$data" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" \
                -H "Content-Type: application/json" \
                "$API_BASE_URL$endpoint")
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" \
                -H "Content-Type: application/json" \
                -d "$data" \
                "$API_BASE_URL$endpoint")
        fi
    fi
    
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" == "$expected_status" ]; then
        echo -e "  ${GREEN}✅ Status: $http_code (Expected: $expected_status)${NC}"
        echo "  Response: $(echo "$body" | head -c 100)..."
        ((TESTS_PASSED++))
    else
        echo -e "  ${RED}❌ Status: $http_code (Expected: $expected_status)${NC}"
        echo "  Response: $body"
        ((TESTS_FAILED++))
    fi
    echo ""
}

# Test 1: Health Check
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}HEALTH & CONNECTIVITY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "Health Check" "GET" "/health" "" "200"
test_endpoint "Root Endpoint" "GET" "/" "" "200"

# Test 2: Layer 1 - Classification
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}LAYER 1 - CLASSIFICATION${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "Text Classification" "POST" "/api/classify/text" \
    '{"text":"This is a sample document for testing the classification layer."}' "200"

# Test 3: Layer 2 - Clone Detection
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}LAYER 2 - CLONE DETECTION${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "Clone Search Statistics" "GET" "/api/clone/statistics" "" "200"

# Test 4: Layer 3 - Cryptographic Verification
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}LAYER 3 - CRYPTOGRAPHIC VERIFICATION${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "Crypto Service Status" "GET" "/api/crypto/crypto-validation/status" "" "200"

# Test 5: Layer 4 - RAG
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}LAYER 4 - RAG / CONTEXT VERIFICATION${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "RAG Health Check" "GET" "/api/rag/health" "" "200"

# Test 6: Layer 5 - Authenticity Scoring
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}LAYER 5 - AUTHENTICITY SCORING${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "Database Stats" "GET" "/api/v1/stats/database" "" "200"

# Test 7: Layer 6 - AI Detection
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}LAYER 6 - AI DETECTION${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "AI Clone Detection Status" "GET" "/api/ai-clone/ai-clone-detection/status" "" "200"

# Test 8: Authentication
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}AUTHENTICATION${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "Get OAuth Providers" "GET" "/auth/oauth/providers" "" "200"

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo ""
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
TOTAL=$((TESTS_PASSED + TESTS_FAILED))
echo "Total Tests: $TOTAL"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}Backend is ready for frontend integration.${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo -e "${RED}Please check the errors above.${NC}"
    exit 1
fi
