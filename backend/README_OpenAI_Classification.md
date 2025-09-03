# OpenAI Document Classification Service

This service provides AI-powered document classification using OpenAI's GPT models. It can classify documents into predefined categories and subcategories with high accuracy.

## Features

- **Single Document Classification**: Classify individual documents
- **Batch Classification**: Process multiple documents at once
- **Comprehensive Categories**: 8 main categories with 10+ subcategories each
- **Confidence Scoring**: Get confidence levels for each classification
- **Detailed Reasoning**: Understand why a document was classified in a particular way
- **Health Monitoring**: Built-in health checks and monitoring

## Categories and Subcategories

### Financial
- Bank Statement, Credit Card Statement, Invoice, Receipt
- Tax Document, Investment Statement, Insurance Document
- Loan Document, Pay Stub, Budget Document

### Legal
- Contract, Legal Agreement, Court Document, Legal Notice
- Power of Attorney, Will, Trust Document, Legal Brief
- Compliance Document, Regulatory Filing

### Medical
- Medical Record, Prescription, Lab Report, Insurance Card
- Medical Bill, Health Certificate, Vaccination Record
- Medical History, Treatment Plan, Diagnostic Report

### Educational
- Diploma, Transcript, Certificate, Academic Record
- Course Material, Research Paper, Thesis, Assignment
- Grade Report, Enrollment Document

### Government
- ID Card, Passport, Driver License, Birth Certificate
- Marriage Certificate, Social Security Card, Voter ID
- Government Form, Official Letter, Permit

### Business
- Business Plan, Proposal, Report, Presentation
- Meeting Minutes, Policy Document, Procedure Manual
- Employee Handbook, Company Policy, Business Contract

### Personal
- Personal Letter, Diary Entry, Personal Note, Journal
- Personal Photo, Personal Document, Personal Record
- Personal Correspondence, Personal Certificate, Personal ID

### Other
- Unknown Document, Miscellaneous, Uncategorized
- Mixed Content, General Document, Other Type

## API Endpoints

### 1. Single Document Classification
```
POST /api/openai/classification/classify
```

**Request Body:**
```json
{
    "text_content": "Document text to classify",
    "confidence_threshold": 0.7
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "category": "Financial",
        "subcategory": "Bank Statement",
        "confidence": 0.95,
        "reasoning": "The text contains banking terminology and transaction details",
        "model_used": "gpt-4o-mini",
        "api_timestamp": 1234567890,
        "input_length": 150,
        "confidence_threshold": 0.7
    }
}
```

### 2. Batch Document Classification
```
POST /api/openai/classification/batch-classify
```

**Request Body:**
```json
{
    "documents": [
        "Document 1 text",
        "Document 2 text",
        "Document 3 text"
    ],
    "confidence_threshold": 0.7
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "classifications": [...],
        "statistics": {
            "total_documents": 3,
            "categories": {...},
            "subcategories": {...},
            "confidence_stats": {...},
            "errors": 0
        }
    }
}
```

### 3. Get Available Categories
```
GET /api/openai/classification/categories
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "categories": {...},
        "total_categories": 8,
        "total_subcategories": 80
    }
}
```

### 4. Health Check
```
GET /api/openai/classification/health
```

**Response:**
```json
{
    "status": "healthy",
    "service": "OpenAI Classification Service",
    "message": "Service is working correctly",
    "test_classification": {...}
}
```

## Setup and Configuration

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Set OpenAI API Key
Create a `.env` file in the backend directory:
```bash
cp env_template.txt .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_actual_api_key_here
```

### 3. Test the Service
```bash
python3 test_openai_classification.py
```

### 4. Start the Backend Server
```bash
python3 app.py
```

## Usage Examples

### Python Client Example
```python
import requests

# Single document classification
response = requests.post('http://localhost:5000/api/openai/classification/classify', 
    json={
        'text_content': 'This is a bank statement for January 2024.',
        'confidence_threshold': 0.8
    }
)

result = response.json()
print(f"Category: {result['data']['category']}")
print(f"Subcategory: {result['data']['subcategory']}")
print(f"Confidence: {result['data']['confidence']}")
```

### cURL Example
```bash
curl -X POST http://localhost:5000/api/openai/classification/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text_content": "Invoice for consulting services",
    "confidence_threshold": 0.7
  }'
```

## Error Handling

The service includes comprehensive error handling:

- **Input Validation**: Checks for required fields and data types
- **API Error Handling**: Gracefully handles OpenAI API errors
- **Response Validation**: Ensures OpenAI responses are valid
- **Fallback Classification**: Uses "Other" category for failed classifications
- **Detailed Logging**: Logs all errors for debugging

## Performance and Cost Optimization

- **Model Selection**: Uses GPT-4o-mini for cost efficiency
- **Temperature Control**: Low temperature (0.1) for consistent results
- **Token Limits**: Configurable max tokens and input truncation
- **Batch Processing**: Efficient batch classification for multiple documents
- **Caching**: Consider implementing Redis caching for repeated classifications

## Monitoring and Analytics

The service provides:

- **Classification Statistics**: Counts, confidence distributions, error rates
- **Health Monitoring**: Real-time service status
- **Performance Metrics**: Response times, success rates
- **Usage Analytics**: Document counts, category distributions

## Security Considerations

- **API Key Protection**: Store API keys in environment variables
- **Input Sanitization**: Validate and sanitize all input text
- **Rate Limiting**: Consider implementing rate limiting for API endpoints
- **Access Control**: Implement authentication for production use

## Troubleshooting

### Common Issues

1. **Missing API Key**: Ensure OPENAI_API_KEY is set in .env file
2. **API Rate Limits**: Check OpenAI API usage and limits
3. **Invalid Input**: Ensure text_content is a non-empty string
4. **Network Issues**: Check internet connectivity and OpenAI API status

### Debug Mode

Enable debug logging by setting the log level:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **Multi-language Support**: Support for non-English documents
- **Custom Categories**: Allow users to define custom categories
- **Model Fine-tuning**: Fine-tune models on specific document types
- **Real-time Processing**: WebSocket support for real-time classification
- **Integration**: Connect with document management systems
