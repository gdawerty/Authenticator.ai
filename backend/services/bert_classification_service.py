# bert_classification_service.py
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel, AutoConfig
import json
import numpy as np
import os

class M4BertClassifier(nn.Module):
    """BERT classifier for document classification"""
    
    def __init__(self, model_name, num_labels, dropout=0.1):
        super().__init__()
        
        self.config = AutoConfig.from_pretrained(
            model_name, 
            output_hidden_states=False,
            output_attentions=False
        )
        
        self.bert = AutoModel.from_pretrained(model_name, config=self.config)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.config.hidden_size, num_labels)
        
        # Initialize classifier weights
        nn.init.xavier_uniform_(self.classifier.weight)
        nn.init.zeros_(self.classifier.bias)
    
    def forward(self, input_ids, attention_mask, token_type_ids=None, labels=None):
        outputs = self.bert(
            input_ids=input_ids, 
            attention_mask=attention_mask, 
            token_type_ids=token_type_ids
        )
        
        cls_output = outputs.last_hidden_state[:, 0]  # CLS token
        cls_output = self.dropout(cls_output)
        logits = self.classifier(cls_output)
        
        return {'logits': logits}

class BERTDocumentClassifier:
    def __init__(self, model_path=None, label_map_path=None):
        """Load trained BERT model for inference"""
        
        # Default paths - using the 138-category hierarchical model
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), '../../BERT/models/best_model.pt')
        if label_map_path is None:
            label_map_path = os.path.join(os.path.dirname(__file__), '../../BERT/models/label_map.json')
        
        # Load label mappings
        with open(label_map_path, 'r') as f:
            label_data = json.load(f)
        
        # Extract the actual label map from the nested structure
        self.label_map = label_data.get('label_map', label_data)
        
        # Create reverse mapping (id -> label)
        self.id_to_label = {int(k): v for k, v in self.label_map.items()}
        
        # Model config
        self.model_name = 'bert-base-uncased'
        self.num_labels = len(self.label_map)
        self.max_length = 512
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Check if model exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"BERT model not found at {model_path}")
        
        # Load model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load the state dict to check actual number of classes
        state_dict = torch.load(model_path, map_location=self.device)
        actual_num_labels = state_dict['classifier.weight'].shape[0]
        
        # Use the actual number of labels from the trained model
        print(f"📊 Label map has {self.num_labels} labels, trained model has {actual_num_labels} labels")
        
        self.model = M4BertClassifier(self.model_name, actual_num_labels)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()
        
        # Update num_labels to match the actual model
        self.num_labels = actual_num_labels
        
        print(f"✅ BERT model loaded: {self.num_labels} categories")
        print(f"📱 Device: {self.device}")
        print(f"🎯 Using trained model: best_model.pt")
    
    def predict(self, text, return_confidence=True):
        """Classify a single document"""
        
        # Clean and truncate text
        text = str(text).strip()[:2000]  # Limit text length
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        # Move to device
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs['logits']
            probabilities = torch.softmax(logits, dim=-1)
            
            # Get prediction
            predicted_id = torch.argmax(probabilities, dim=-1).item()
            confidence = torch.max(probabilities).item()
            
            predicted_label = self.id_to_label.get(predicted_id, f"unknown_{predicted_id}")
        
        if return_confidence:
            return {
                'prediction': predicted_label,
                'confidence': confidence,
                'predicted_id': predicted_id,
                'method': 'BERT'
            }
        else:
            return predicted_label
    
    def predict_batch(self, texts, batch_size=8):
        """Classify multiple documents"""
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_results = [self.predict(text) for text in batch]
            results.extend(batch_results)
        
        return results
    
    def get_categories(self):
        """Get all available categories"""
        return list(self.id_to_label.values())
    
    def get_category_count(self):
        """Get number of categories"""
        return self.num_labels

# Global classifier instance (lazy loading)
_classifier = None

def get_bert_classifier():
    """Get or create BERT classifier instance"""
    global _classifier
    if _classifier is None:
        _classifier = BERTDocumentClassifier()
    return _classifier

def classify_document_bert(text):
    """Main function to classify document with BERT"""
    classifier = get_bert_classifier()
    return classifier.predict(text)

def classify_documents_batch_bert(texts):
    """Classify multiple documents with BERT"""
    classifier = get_bert_classifier()
    return classifier.predict_batch(texts)

def get_model_info():
    """Get BERT model information"""
    try:
        classifier = get_bert_classifier()
        return {
            'status': 'healthy',
            'model_name': classifier.model_name,
            'num_labels': classifier.num_labels,
            'device': str(classifier.device),
            'categories': classifier.get_categories(),
            'max_length': classifier.max_length
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }