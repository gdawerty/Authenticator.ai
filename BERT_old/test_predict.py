#!/usr/bin/env python3
"""
Test the predict function with the hierarchical BERT model
"""

import torch
import torch.nn.functional as F
import json
import os
from transformers import AutoTokenizer, AutoModel, AutoConfig
from torch import nn

# Check if model exists
model_path = 'hierarchical_artifacts/best_model.pt'
label_map_path = 'hierarchical_artifacts/label_map.json'

if not os.path.exists(model_path):
    print("❌ No trained model found! Please train the model first.")
    exit()

# Load label map
try:
    with open(label_map_path, 'r') as f:
        label_map = json.load(f)
    print(f"✅ Loaded label map with {len(label_map)} categories")
    print("Available categories:")
    for idx, label in label_map.items():
        print(f"  {idx}: {label}")
except FileNotFoundError:
    print("❌ No label map found! Please train the model first.")
    exit()

# Model configuration (should match training config)
MODEL_NAME = 'bert-base-uncased'
MAX_LEN = 256
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
num_labels = len(label_map)

print(f"📊 Model config: {num_labels} labels, device: {DEVICE}")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# Define the same model architecture as training
class BertClassifier(nn.Module):
    def __init__(self, model_name, num_labels, dropout=0.1):
        super().__init__()
        self.config = AutoConfig.from_pretrained(model_name, output_hidden_states=False)
        self.bert = AutoModel.from_pretrained(model_name, config=self.config)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.config.hidden_size, num_labels)
    
    def forward(self, input_ids, attention_mask, token_type_ids=None, labels=None):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        cls = outputs.last_hidden_state[:,0]
        logits = self.classifier(self.dropout(cls))
        if labels is not None:
            return logits, labels
        return logits

# Load the trained model
model = BertClassifier(MODEL_NAME, num_labels).to(DEVICE)
model.load_state_dict(torch.load(model_path, map_location=DEVICE))
model.eval()

print("✅ Model loaded successfully!")

def predict(texts, batch_size=32, return_labels=True):
    """Predict function from the notebook"""
    model.eval()
    preds_all, probs_all = [], []
    
    for i in range(0, len(texts), batch_size):
        chunk = texts[i:i+batch_size]
        enc = tokenizer(chunk, truncation=True, padding=True, max_length=MAX_LEN, return_tensors='pt')
        enc = {k: v.to(DEVICE) for k,v in enc.items()}
        
        with torch.no_grad():
            logits = model(**enc)
        
        probs = F.softmax(logits, dim=-1).cpu().numpy()
        preds = probs.argmax(axis=1)
        
        if return_labels:
            preds_lbl = [label_map[str(int(p))] for p in preds]
            preds_all.extend(preds_lbl)
        else:
            preds_all.extend(preds.tolist())
        
        probs_all.extend(probs.tolist())
    
    return preds_all, probs_all

# Test samples
test_texts = [
    "This is a student transcript showing grades from the 2023 academic year.",
    "Insurance claim for automobile accident on Main Street.",
    "Legal contract between two parties for business agreement.",
    "Math problem: What is 15 + 27?",
    "Science question: What is the chemical formula for water?",
    "Movie review: This film was absolutely fantastic with great acting.",
    "Restaurant review: The food was delicious and the service was excellent.",
    "Deepfake detection analysis of video content.",
    "Receipt from grocery store purchase.",
    "News article about current events."
]

print("\n🧪 Testing predict function...")
print("=" * 50)

try:
    predictions, probabilities = predict(test_texts)
    
    print("\n📊 Prediction Results:")
    print("=" * 50)
    
    for i, (text, pred, prob) in enumerate(zip(test_texts, predictions, probabilities)):
        print(f"\n{i+1}. Text: {text[:100]}...")
        print(f"   Prediction: {pred}")
        print(f"   Confidence: {max(prob):.3f}")
        
        # Show top 3 predictions
        top_indices = prob.argsort()[-3:][::-1]
        print("   Top 3 predictions:")
        for idx in top_indices:
            confidence = prob[idx]
            category = label_map[str(idx)]
            print(f"     - {category}: {confidence:.3f}")
    
    print(f"\n✅ Successfully tested {len(test_texts)} samples!")
    
except Exception as e:
    print(f"❌ Error during prediction: {e}")
    import traceback
    traceback.print_exc()

# Interactive testing
print("\n🎯 Interactive Testing")
print("=" * 50)
print("Enter your own text to test (or 'quit' to exit):")

while True:
    try:
        user_text = input("\nEnter text: ").strip()
        if user_text.lower() == 'quit':
            break
        if not user_text:
            continue
            
        pred, prob = predict([user_text])
        print(f"Prediction: {pred[0]}")
        print(f"Confidence: {max(prob[0]):.3f}")
        
        # Show top 3
        top_indices = prob[0].argsort()[-3:][::-1]
        print("Top 3 predictions:")
        for idx in top_indices:
            confidence = prob[0][idx]
            category = label_map[str(idx)]
            print(f"  - {category}: {confidence:.3f}")
            
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Error: {e}")

print("\n👋 Testing complete!")
