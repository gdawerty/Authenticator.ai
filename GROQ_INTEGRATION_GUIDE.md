# 🚀 Groq Cloud Integration Guide

## Overview

Authenticator.AI now integrates with **Groq Cloud** to generate intelligent explanations for each layer of the document analysis pipeline using **Mixtral-8x7B** or **Mistral-7B** models.

### Key Features

✅ **Free API Access** - Groq Cloud offers free API access for both Mistral-7B and Mixtral-8x7B models
✅ **Fast Inference** - Ultra-low latency responses (< 100ms)
✅ **Layer-Specific Explanations** - Unique explanations for each of the 7 layers
✅ **Comprehensive Summaries** - Overall document authenticity assessment
✅ **Frontend Integration** - Ready for UI tooltips and detailed explanations

---

## Setup Instructions

### 1. Get Groq API Key

1. Visit **[https://console.groq.com](https://console.groq.com)**
2. Sign up for a free account
3. Go to **API Keys** section
4. Create a new API key
5. Copy your API key (starts with `gsk_`)

### 2. Configure Backend

Create a `.env` file in the `backend/` directory:

```bash
# Copy from env_template.txt
cp backend/env_template.txt backend/.env

# Edit .env and add your Groq API key
GROQ_API_KEY=gsk_your_actual_api_key_here
GROQ_MODEL=mixtral-8x7b-32768
```

### 3. In Docker

For Docker Compose, add the environment variable to `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - GROQ_API_KEY=gsk_your_actual_api_key_here
      - GROQ_MODEL=mixtral-8x7b-32768
```

### 4. Test Connection

```bash
# Test explanation service
python3 -m backend.services.groq_explanation_service

# Expected output:
# Layer 1 Explanation: ...
# Layer 2 Explanation: ...
# Layer 6 Explanation: ...
```

---

## API Endpoints

### Get Layer Explanation

**Endpoint:** `POST /api/explanations/layer/<layer_number>`

**Request:**
```json
{
  "layer_result": {
    "result": "text",
    "confidence": 0.97,
    "filename": "document.pdf"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "layer": 1,
  "explanation": "The document was classified as text based on consistent sentence structure, no embedded image data, and UTF-8 encoded content across 98% of the file.",
  "timestamp": "2025-10-24T10:30:00.000Z"
}
```

### Get Comprehensive Explanation

**Endpoint:** `POST /api/explanations/comprehensive`

**Request:**
```json
{
  "analysis_result": {
    "layerResults": [...],
    "finalScore": 87,
    "classification": "Authentic"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "comprehensive_explanation": "This document demonstrates strong authenticity indicators with high integrity, consistent formatting, and contextual alignment with verified sources. Minor AI-likeness patterns detected but outweighed by human writing characteristics.",
  "timestamp": "2025-10-24T10:30:00.000Z"
}
```

### Add Explanations to Analysis

**Endpoint:** `POST /api/explanations/with-explanations`

**Request:**
```json
{
  "analysis_result": {
    "layerResults": [...],
    "finalScore": 87
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "analysis_id": "analysis_123",
    "final_score": 87,
    "classification": "Authentic",
    "comprehensive_explanation": "...",
    "layers": [
      {
        "layer_number": 1,
        "layer_type": "classification",
        "result": "text",
        "explanation": "...",
        "confidence": 0.97
      },
      ...
    ],
    "explanation_metadata": {
      "generated_at": "2025-10-24T10:30:00.000Z",
      "explanation_model": "mixtral-8x7b-32768",
      "explanation_provider": "Groq Cloud",
      "explanation_enabled": true
    }
  },
  "timestamp": "2025-10-24T10:30:00.000Z"
}
```

### Health Check

**Endpoint:** `GET /api/explanations/health`

**Response:**
```json
{
  "status": "healthy",
  "explanation_service": "Groq Cloud",
  "model": "mixtral-8x7b-32768",
  "api_configured": true,
  "timestamp": "2025-10-24T10:30:00.000Z"
}
```

---

## Layer Explanations

Each of the 7 layers generates context-specific explanations:

### Layer 1: Classification
- Key indicators for document type
- File structure analysis
- Content characteristics

### Layer 2: Clone Detection
- Similarity score interpretation
- Matched sections analysis
- Plagiarism risk assessment

### Layer 3: Cryptographic Verification
- Hash verification results
- Document alteration detection
- Timestamp relevance

### Layer 4: RAG Context Verification
- Source alignment analysis
- Factual deviation identification
- Content verification results

### Layer 5: Authenticity Scoring
- Score interpretation
- Contributing factors
- Confidence assessment

### Layer 6: AI Detection
- AI generation probability
- Pattern analysis
- Writing style assessment

---

## Implementation Details

### Service Files

1. **`groq_explanation_service.py`**
   - Core Groq API integration
   - Layer-specific explanation generators
   - API request/response handling

2. **`layer_explanation_integrator.py`**
   - Integration with analysis pipeline
   - Result formatting for frontend
   - Explanation aggregation

3. **`explanation_routes.py`**
   - Flask-RESTx routes
   - API endpoints
   - Health checks

### Configuration

**`config/config.py`**
```python
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
```

---

## Usage Examples

### Python Integration

```python
from backend.services.groq_explanation_service import get_groq_service

groq_service = get_groq_service()

# Generate Layer 1 explanation
layer_1_result = {
    'result': 'text',
    'confidence': 0.97,
    'filename': 'document.pdf'
}
explanation = groq_service.generate_layer_1_explanation(layer_1_result)
print(explanation)
```

### With Explanation Integrator

```python
from backend.services.layer_explanation_integrator import get_explanation_integrator

integrator = get_explanation_integrator()

# Add explanations to analysis result
enhanced_result = integrator.add_explanations_to_result(analysis_result)

# Format for frontend
formatted_result = integrator.format_analysis_with_explanations(enhanced_result)
```

---

## Frontend Integration

### Display Explanations

```typescript
// Frontend type definition
interface LayerWithExplanation {
  layer_number: number;
  layer_type: string;
  result: any;
  explanation: string;
  confidence: number;
  timestamp: string;
}

// Fetch explanations
const response = await fetch('/api/explanations/with-explanations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ analysis_result })
});

const { data } = await response.json();

// Display comprehensive explanation
console.log(data.comprehensive_explanation);

// Display layer explanations with tooltips
data.layers.forEach(layer => {
  console.log(`Layer ${layer.layer_number}: ${layer.explanation}`);
});
```

### Tooltip Implementation

```typescript
// Add explanation to layer result display
<div className="layer-result">
  <h3>Layer {layer.layer_number}</h3>
  <p>{layer.result}</p>
  <Tooltip title={layer.explanation}>
    <InfoIcon />
  </Tooltip>
</div>
```

---

## Troubleshooting

### API Key Not Set
```
⚠️ Warning: GROQ_API_KEY not set. Explanations will be limited.
```
**Solution:** Add `GROQ_API_KEY` to `.env` file or environment variables

### Invalid API Key
```
⚠️ Groq API error: 401
```
**Solution:** Verify API key is correct at https://console.groq.com/keys

### Rate Limiting
```
⚠️ Groq API error: 429
```
**Solution:** Free tier has rate limits. Wait and retry, or consider paid plan

### Timeout
```
⚠️ Groq API timeout
```
**Solution:** Groq Cloud may be experiencing high load. Retry with exponential backoff

---

## Performance Notes

- **Latency:** Typically < 100ms per layer explanation
- **Cost:** Free tier available (no credit card required)
- **Rate Limits:** Varies by plan (free tier: ~30 requests/minute)
- **Model:** Mixtral-8x7B is faster than Mistral-7B, recommended for production

---

## Model Comparison

| Model | Speed | Quality | Cost |
|-------|-------|---------|------|
| Mistral-7B | Very Fast | Good | Free |
| Mixtral-8x7B | Fast | Excellent | Free |

**Recommendation:** Use `mixtral-8x7b-32768` for best quality

---

## Production Deployment

For production:

1. ✅ Set `GROQ_API_KEY` in environment secrets
2. ✅ Monitor API usage and rate limits
3. ✅ Implement caching for repeated explanations
4. ✅ Add error handling for API failures
5. ✅ Consider paid plan for higher rate limits

---

## Support

- **Groq Documentation:** https://console.groq.com/docs
- **API Keys:** https://console.groq.com/keys
- **Status:** https://status.groq.com

---

**Last Updated:** October 24, 2025
**Integration Status:** ✅ Complete and Ready for Use
