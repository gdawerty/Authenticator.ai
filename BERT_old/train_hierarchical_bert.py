#!/usr/bin/env python3
"""
Hierarchical BERT Training Script
Uses the new hierarchical data with 5 meaningful classes
"""

import os
import json
import random
import numpy as np
import pandas as pd
from collections import Counter

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.preprocessing import LabelEncoder

from transformers import AutoTokenizer, AutoModel, AutoConfig, get_linear_schedule_with_warmup

# Set random seeds
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

# Device setup
DEVICE = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
print(f"🖥️ Using device: {DEVICE}")

class HierarchicalTextDataset(Dataset):
    def __init__(self, df, tokenizer, max_len=256):
        self.df = df.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_len = max_len
        
    def __len__(self):
        return len(self.df)
        
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        enc = self.tokenizer(
            str(row['text']), 
            truncation=True, 
            padding='max_length', 
            max_length=self.max_len, 
            return_tensors='pt'
        )
        item = {k: v.squeeze(0) for k, v in enc.items()}
        item['labels'] = torch.tensor(int(row['label']), dtype=torch.long)
        return item

class HierarchicalBertClassifier(nn.Module):
    def __init__(self, model_name, num_labels, dropout=0.1):
        super().__init__()
        self.config = AutoConfig.from_pretrained(model_name, output_hidden_states=False)
        self.bert = AutoModel.from_pretrained(model_name, config=self.config)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.config.hidden_size, num_labels)
        
    def forward(self, input_ids, attention_mask, token_type_ids=None, labels=None):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        cls = outputs.last_hidden_state[:, 0]
        logits = self.classifier(self.dropout(cls))
        if labels is not None:
            return logits, labels
        return logits

def load_hierarchical_data():
    """Load the hierarchical data we created"""
    print("📥 Loading hierarchical data...")
    
    # Load data
    train_df = pd.read_csv('hierarchical_train.csv')
    val_df = pd.read_csv('hierarchical_val.csv')
    test_df = pd.read_csv('hierarchical_test.csv')
    
    print(f"📊 Raw data shapes - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    
    # Filter out empty hierarchical labels
    train_df = train_df.dropna(subset=['hierarchical_label'])
    val_df = val_df.dropna(subset=['hierarchical_label'])
    test_df = test_df.dropna(subset=['hierarchical_label'])
    
    train_df = train_df[train_df['hierarchical_label'].str.len() > 0]
    val_df = val_df[val_df['hierarchical_label'].str.len() > 0]
    test_df = test_df[test_df['hierarchical_label'].str.len() > 0]
    
    print(f"📊 After filtering - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    
    # Label encoding
    print("🏷️ Encoding hierarchical labels...")
    le = LabelEncoder()
    train_df['label'] = le.fit_transform(train_df['hierarchical_label'])
    val_df['label'] = le.transform(val_df['hierarchical_label'])
    test_df['label'] = le.transform(test_df['hierarchical_label'])
    
    # Create label map
    label_map = {int(i): cls for i, cls in enumerate(le.classes_)}
    
    # Save label map
    os.makedirs('hierarchical_artifacts', exist_ok=True)
    with open('hierarchical_artifacts/label_map.json', 'w') as f:
        json.dump(label_map, f, indent=2)
    
    print(f"✅ Encoded {len(label_map)} hierarchical classes:")
    for i, label in label_map.items():
        print(f"  {i}: {label}")
    
    # Prepare text data
    train_df['text'] = train_df['cleaned_text'].astype(str)
    val_df['text'] = val_df['cleaned_text'].astype(str)
    test_df['text'] = test_df['cleaned_text'].astype(str)
    
    return train_df, val_df, test_df, len(label_map)

def train_hierarchical_model():
    """Train the hierarchical BERT model"""
    
    # Configuration
    MODEL_NAME = 'bert-base-uncased'
    MAX_LEN = 256
    BATCH_SIZE = 16
    LR = 2e-5
    EPOCHS = 4
    WARMUP_RATIO = 0.1
    PATIENCE = 3
    WEIGHT_DECAY = 0.01
    
    print("🚀 Starting Hierarchical BERT Training!")
    print("=" * 60)
    
    # Load data
    train_df, val_df, test_df, num_labels = load_hierarchical_data()
    
    # Initialize tokenizer
    print("🔤 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    # Create datasets
    print("📦 Creating datasets...")
    train_ds = HierarchicalTextDataset(train_df, tokenizer, MAX_LEN)
    val_ds = HierarchicalTextDataset(val_df, tokenizer, MAX_LEN)
    test_ds = HierarchicalTextDataset(test_df, tokenizer, MAX_LEN)
    
    # Create data loaders
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE)
    
    print(f"📊 Dataset sizes - Train: {len(train_ds)}, Val: {len(val_ds)}, Test: {len(test_ds)}")
    
    # Initialize model
    print("🤖 Initializing BERT model...")
    model = HierarchicalBertClassifier(MODEL_NAME, num_labels).to(DEVICE)
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"📊 Total parameters: {total_params:,}")
    print(f"📊 Trainable parameters: {trainable_params:,}")
    
    # Calculate class weights
    print("⚖️ Calculating class weights...")
    labels = []
    for batch in train_loader:
        labels.extend(batch['labels'].tolist())
        if len(labels) >= 10000:  # Sample first 10k for speed
            break
    
    cnt = Counter(labels)
    total = sum(cnt.values())
    class_weights = torch.tensor([total/(num_labels*cnt[i]) for i in range(num_labels)], dtype=torch.float32).to(DEVICE)
    print(f"✅ Class weights calculated")
    
    # Optimizer and scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    num_training_steps = len(train_loader) * EPOCHS
    num_warmup_steps = int(WARMUP_RATIO * num_training_steps)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps, num_training_steps)
    loss_fn = nn.CrossEntropyLoss(weight=class_weights)
    
    # Training loop
    print("🎯 Starting training...")
    best_f1, patience = -1.0, 0
    history = []
    
    for epoch in range(1, EPOCHS + 1):
        print(f"\n📅 Epoch {epoch}/{EPOCHS}")
        
        # Training
        model.train()
        train_losses, train_preds, train_labels = [], [], []
        
        for batch_idx, batch in enumerate(train_loader):
            input_ids = batch['input_ids'].to(DEVICE)
            attention_mask = batch['attention_mask'].to(DEVICE)
            token_type_ids = batch.get('token_type_ids')
            if token_type_ids is not None:
                token_type_ids = token_type_ids.to(DEVICE)
            labels = batch['labels'].to(DEVICE)
            
            optimizer.zero_grad()
            logits, _ = model(input_ids, attention_mask, token_type_ids, labels)
            loss = loss_fn(logits, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            
            train_losses.append(loss.item())
            train_preds.extend(logits.argmax(-1).detach().cpu().numpy())
            train_labels.extend(labels.detach().cpu().numpy())
            
            # Progress indicator
            if batch_idx % 50 == 0:
                print(f"  📊 Batch {batch_idx}/{len(train_loader)} - Loss: {loss.item():.4f}")
        
        # Calculate training metrics
        tr_acc = accuracy_score(train_labels, train_preds)
        tr_f1 = f1_score(train_labels, train_preds, average='macro')
        
        # Validation
        print("🔍 Validating...")
        model.eval()
        val_losses, val_preds, val_labels = [], [], []
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(DEVICE)
                attention_mask = batch['attention_mask'].to(DEVICE)
                token_type_ids = batch.get('token_type_ids')
                if token_type_ids is not None:
                    token_type_ids = token_type_ids.to(DEVICE)
                labels = batch['labels'].to(DEVICE)
                
                logits, _ = model(input_ids, attention_mask, token_type_ids, labels)
                loss = loss_fn(logits, labels)
                
                val_losses.append(loss.item())
                val_preds.extend(logits.argmax(-1).detach().cpu().numpy())
                val_labels.extend(labels.detach().cpu().numpy())
        
        va_acc = accuracy_score(val_labels, val_preds)
        va_f1 = f1_score(val_labels, val_preds, average='macro')
        
        print(f"📊 Epoch {epoch}: Train Loss: {np.mean(train_losses):.4f}, Val Loss: {np.mean(val_losses):.4f}")
        print(f"📊 Train F1: {tr_f1:.4f}, Val F1: {va_f1:.4f}")
        
        # Save history
        history.append({
            'epoch': epoch,
            'train_loss': float(np.mean(train_losses)),
            'val_loss': float(np.mean(val_losses)),
            'train_acc': float(tr_acc),
            'val_acc': float(va_acc),
            'train_f1': float(tr_f1),
            'val_f1': float(va_f1)
        })
        
        # Save checkpoint
        with open('hierarchical_artifacts/history.json', 'w') as f:
            json.dump(history, f, indent=2)
        
        # Early stopping
        if va_f1 > best_f1:
            best_f1 = va_f1
            patience = 0
            torch.save(model.state_dict(), 'hierarchical_artifacts/best_model.pt')
            print(f"💾 New best model saved! F1: {best_f1:.4f}")
        else:
            patience += 1
            if patience >= PATIENCE:
                print(f"⏹️ Early stopping triggered after {PATIENCE} epochs")
                break
    
    # Final evaluation
    print("\n🧪 Final evaluation on test set...")
    model.load_state_dict(torch.load('hierarchical_artifacts/best_model.pt', map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    
    test_preds, test_labels = [], []
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch['input_ids'].to(DEVICE)
            attention_mask = batch['attention_mask'].to(DEVICE)
            token_type_ids = batch.get('token_type_ids')
            if token_type_ids is not None:
                token_type_ids = token_type_ids.to(DEVICE)
            labels = batch['labels'].to(DEVICE)
            
            logits, _ = model(input_ids, attention_mask, token_type_ids, labels)
            test_preds.extend(logits.argmax(-1).detach().cpu().numpy())
            test_labels.extend(labels.detach().cpu().numpy())
    
    # Calculate final metrics
    acc = accuracy_score(test_labels, test_preds)
    f1m = f1_score(test_labels, test_preds, average='macro')
    
    print(f"\n🎉 Final Results:")
    print(f"📊 Test Accuracy: {acc:.4f}")
    print(f"📊 Test F1 Macro: {f1m:.4f}")
    
    # Save final results
    results = {
        'test_accuracy': acc,
        'test_f1_macro': f1m,
        'best_val_f1': best_f1,
        'total_epochs': len(history)
    }
    
    with open('hierarchical_artifacts/final_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to: hierarchical_artifacts/")
    print("🎉 Hierarchical BERT training complete!")

if __name__ == "__main__":
    train_hierarchical_model()
