# RunPod Fast-DetectGPT Setup Guide

This guide will help you set up a RunPod instance to run Fast-DetectGPT for high-accuracy AI detection.

## Quick Setup

### 1. Create RunPod Account
- Go to [runpod.io](https://www.runpod.io/)
- Sign up for an account
- Add payment method (GPU instances cost ~$0.50-2.00/hour)

### 2. Deploy Fast-DetectGPT Pod

#### Option A: Use Pre-built Docker Image (Recommended)
```bash
# Use this Docker image in RunPod:
docker pull pytorch/pytorch:2.0.1-cuda11.7-cudnn8-devel

# Or create custom image with our setup script
```

#### Option B: Manual Setup Script
Create a new Pod with the following startup script:

```bash
#!/bin/bash
# RunPod Fast-DetectGPT Setup Script

# Update system
apt-get update && apt-get install -y git wget curl

# Clone Fast-DetectGPT
cd /workspace
git clone https://github.com/baoguangsheng/fast-detect-gpt.git
cd fast-detect-gpt

# Install Python dependencies
pip install torch numpy transformers==4.28.1 datasets==2.12.0 matplotlib tqdm openai nltk scipy flask flask-cors

# Download recommended models (this will take time!)
python -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

print('Downloading GPT-Neo 2.7B...')
tokenizer = AutoTokenizer.from_pretrained('EleutherAI/gpt-neo-2.7B')
model = AutoModelForCausalLM.from_pretrained('EleutherAI/gpt-neo-2.7B', torch_dtype=torch.float16)
print('GPT-Neo 2.7B downloaded successfully!')

print('Downloading Falcon 7B...')
try:
    tokenizer = AutoTokenizer.from_pretrained('tiiuae/falcon-7b')
    model = AutoModelForCausalLM.from_pretrained('tiiuae/falcon-7b', torch_dtype=torch.float16)
    print('Falcon 7B downloaded successfully!')
except:
    print('Falcon 7B failed, continuing with GPT-Neo only')
"

# Create API server
cat > /workspace/fast-detect-api.py << 'EOF'
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import torch
import argparse

# Add scripts to path
sys.path.append('/workspace/fast-detect-gpt/scripts')
from local_infer import FastDetectGPT

app = Flask(__name__)
CORS(app)

# Initialize Fast-DetectGPT
print("Loading Fast-DetectGPT...")
args = argparse.Namespace(
    sampling_model_name='EleutherAI/gpt-neo-2.7B',
    scoring_model_name='EleutherAI/gpt-neo-2.7B',
    device='cuda' if torch.cuda.is_available() else 'cpu',
    cache_dir='/workspace/model_cache'
)
detector = FastDetectGPT(args)
print("Fast-DetectGPT loaded successfully!")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "model": "fast-detect-gpt"})

@app.route('/detect', methods=['POST'])
def detect():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Run detection
        discrepancy_score = detector.compute_crit(text)
        
        # Calculate probability
        mu0 = detector.classifier['mu0']
        sigma0 = detector.classifier['sigma0']
        mu1 = detector.classifier['mu1']
        sigma1 = detector.classifier['sigma1']
        
        from local_infer import compute_prob_norm
        ai_probability = compute_prob_norm(discrepancy_score, mu0, sigma0, mu1, sigma1)
        
        return jsonify({
            "ai_probability": float(ai_probability),
            "discrepancy_score": float(discrepancy_score),
            "model": "gpt-neo-2.7B",
            "is_ai_generated": ai_probability > 0.5
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
EOF

# Start the API server
python /workspace/fast-detect-api.py
```

### 3. Configure Environment Variables

After your RunPod is running, add these to your local environment:

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export RUNPOD_FAST_DETECT_ENDPOINT="https://YOUR_POD_ID-8000.proxy.runpod.net"
export RUNPOD_API_KEY="your_runpod_api_key"
```

### 4. Test Connection

```bash
# Test the RunPod endpoint
curl -X GET "https://YOUR_POD_ID-8000.proxy.runpod.net/health"

# Test AI detection
curl -X POST "https://YOUR_POD_ID-8000.proxy.runpod.net/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "Furthermore, it is important to note that artificial intelligence systems require careful consideration of various factors."}'
```

## Model Options

### Recommended Models (in order of accuracy):
1. **falcon-7b + falcon-7b-instruct** (Best accuracy, ~12GB VRAM)
2. **gpt-neo-2.7B + gpt-neo-2.7B** (Good accuracy, ~6GB VRAM)
3. **gpt-neo-1.3B + gpt-neo-1.3B** (Fast, ~3GB VRAM)

### GPU Requirements:
- **RTX 4090/A100**: Can run Falcon 7B models
- **RTX 3080/3090**: Can run GPT-Neo 2.7B models
- **RTX 3060**: Can run GPT-Neo 1.3B models

## Cost Estimation

- **GPU Pod (RTX 4090)**: ~$1.50/hour
- **GPU Pod (RTX 3080)**: ~$0.80/hour
- **Storage**: ~$0.10/GB/month

**Monthly cost for 8 hours/day usage**: ~$240-360

## Alternative: Hugging Face Spaces

For lower cost, consider deploying on Hugging Face Spaces with GPU:
- Create a Space with GPU ($1.05/hour when running)
- Use the same setup script
- Only pay when processing requests

## Integration

Once your RunPod is running:

1. Set the environment variables in your backend
2. Restart your Authenticator.ai backend
3. The AI Detection layer will automatically use RunPod when available
4. Falls back to enhanced heuristics when RunPod is offline

## Monitoring

- Check RunPod dashboard for GPU usage
- Monitor API response times
- Set up auto-stop when not in use to save costs
