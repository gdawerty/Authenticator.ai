"""
BERT Model for Document Classification
"""

import torch
import torch.nn as nn
from transformers import AutoModel, AutoConfig
import logging

logger = logging.getLogger(__name__)

class BERTDocumentClassifier(nn.Module):
    """BERT-based document classifier"""
    
    def __init__(self, model_name, num_classes, dropout=0.1):
        super(BERTDocumentClassifier, self).__init__()
        
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)
        
        # Freeze BERT layers (optional - can be unfrozen for fine-tuning)
        # for param in self.bert.parameters():
        #     param.requires_grad = False
        
        logger.info(f"🤖 Initialized BERT classifier with {num_classes} output classes")
    
    def forward(self, input_ids, attention_mask, labels=None):
        """Forward pass"""
        
        # Get BERT outputs
        bert_outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # Use [CLS] token representation for classification
        pooled_output = bert_outputs.pooler_output
        
        # Apply dropout and classification
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        
        outputs = (logits,)
        
        if labels is not None:
            # Calculate loss
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, logits.size(-1)), labels.view(-1))
            outputs = (loss,) + outputs
        
        return outputs
    
    def get_embeddings(self, input_ids, attention_mask):
        """Get BERT embeddings for feature extraction"""
        with torch.no_grad():
            bert_outputs = self.bert(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            return bert_outputs.pooler_output
