#!/usr/bin/env python3
"""
ULTRA-OPTIMIZED BERT Training Script for Authentia.ai Document Classification
Optimized for fast CSV loading and memory efficiency
"""

import os
import json
import argparse
from collections import Counter
import gc

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.preprocessing import LabelEncoder

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel, AutoConfig, get_linear_schedule_with_warmup

# ---------------------------
# OPTIMIZED UTILITIES
# ---------------------------
def set_seed(seed: int):
    import random
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)

def optimize_pandas():
    """Optimize pandas for faster CSV loading"""
    pd.options.mode.chained_assignment = None
    pd.options.mode.sim_interactive = False

class OptimizedTextDataset(Dataset):
    def __init__(self, df, tokenizer, max_len=256):
        # Convert to numpy arrays for faster access
        self.texts = df['text'].values
        self.labels = df['label'].values
        self.tokenizer = tokenizer
        self.max_len = max_len
        
    def __len__(self): 
        return len(self.texts)
    
    def __getitem__(self, i):
        # Use numpy array indexing for speed
        text = str(self.texts[i])
        label = int(self.labels[i])
        
        enc = self.tokenizer(
            text, 
            truncation=True, 
            padding='max_length', 
            max_length=self.max_len, 
            return_tensors='pt'
        )
        item = {k: v.squeeze(0) for k, v in enc.items()}
        item['labels'] = torch.tensor(label, dtype=torch.long)
        return item

class BertClassifier(nn.Module):
    def __init__(self, model_name: str, num_labels: int, dropout: float=0.1):
        super().__init__()
        self.config = AutoConfig.from_pretrained(model_name, output_hidden_states=False)
        self.bert = AutoModel.from_pretrained(model_name, config=self.config)
        self.drop = nn.Dropout(dropout)
        self.fc = nn.Linear(self.config.hidden_size, num_labels)
        
    def forward(self, input_ids, attention_mask, token_type_ids=None, labels=None):
        out = self.bert(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        cls = out.last_hidden_state[:,0]
        logits = self.fc(self.drop(cls))
        if labels is not None: 
            return logits, labels
        return logits

def fast_csv_loader(file_path, text_col, label_col, chunk_size=10000):
    """Ultra-fast CSV loader with chunking and memory optimization"""
    print(f"🚀 Loading {file_path} in chunks of {chunk_size}...")
    
    # Use only the columns we need
    usecols = [text_col, label_col]
    
    # Optimized CSV reading
    chunks = []
    total_rows = 0
    
    for chunk in pd.read_csv(
        file_path, 
        usecols=usecols,
        chunksize=chunk_size,
        low_memory=False,
        dtype={text_col: 'string', label_col: 'string'},
        engine='c'  # Use C engine for speed
    ):
        # Clean and process chunk immediately
        chunk = chunk.dropna(subset=[text_col, label_col])
        chunk = chunk[chunk[text_col].str.len() > 0]
        chunk = chunk[chunk[label_col].str.len() > 0]
        
        chunks.append(chunk)
        total_rows += len(chunk)
        
        if len(chunks) % 5 == 0:
            print(f"  📊 Loaded {total_rows:,} rows so far...")
    
    print(f"✅ Total rows loaded: {total_rows:,}")
    
    # Concatenate all chunks
    df = pd.concat(chunks, ignore_index=True)
    del chunks  # Free memory
    gc.collect()
    
    return df

def make_loaders_optimized(args):
    """Optimized data loading with memory management"""
    print("🚀 Starting optimized data loading...")
    
    # Load training data
    print("📥 Loading training data...")
    train_df = fast_csv_loader(args.train_path, args.text_col, args.label_col)
    
    # Load validation data
    print("📥 Loading validation data...")
    val_df = fast_csv_loader(args.val_path, args.text_col, args.label_col)
    
    # Load test data
    print("📥 Loading test data...")
    test_df = fast_csv_loader(args.test_path, args.text_col, args.label_col)
    
    print(f"📊 Dataset sizes - Train: {len(train_df):,}, Val: {len(val_df):,}, Test: {len(test_df):,}")
    
    # Label encoding
    print("🏷️  Encoding labels...")
    le = LabelEncoder()
    train_df['label'] = le.fit_transform(train_df[args.label_col])
    val_df['label'] = le.transform(val_df[args.label_col])
    test_df['label'] = le.transform(test_df[args.label_col])
    
    # Save label mapping
    os.makedirs(args.out_dir, exist_ok=True)
    label_map = {int(i): c for i, c in enumerate(le.classes_)}
    with open(os.path.join(args.out_dir, 'label_map.json'), 'w') as f:
        json.dump(label_map, f, indent=2)
    
    print(f"✅ Labels encoded: {len(label_map)} classes")
    
    # Convert to numpy arrays for speed
    train_df['text'] = train_df[args.text_col].astype(str)
    val_df['text'] = val_df[args.text_col].astype(str)
    test_df['text'] = test_df[args.text_col].astype(str)
    
    num_labels = len(label_map)
    
    # Initialize tokenizer
    print("🔤 Loading tokenizer...")
    tok = AutoTokenizer.from_pretrained(args.model_name)
    
    # Create datasets
    print("📦 Creating datasets...")
    train_ds = OptimizedTextDataset(train_df, tok, args.max_len)
    val_ds = OptimizedTextDataset(val_df, tok, args.max_len)
    test_ds = OptimizedTextDataset(test_df, tok, args.max_len)
    
    # Create data loaders with optimized settings
    train_loader = DataLoader(
        train_ds, 
        batch_size=args.batch_size, 
        shuffle=True,
        num_workers=0,  # Set to 0 for macOS compatibility
        pin_memory=False  # Disable for macOS
    )
    val_loader = DataLoader(
        val_ds, 
        batch_size=args.batch_size,
        num_workers=0,
        pin_memory=False
    )
    test_loader = DataLoader(
        test_ds, 
        batch_size=args.batch_size,
        num_workers=0,
        pin_memory=False
    )
    
    # Free memory
    del train_df, val_df, test_df
    gc.collect()
    
    return train_loader, val_loader, test_loader, num_labels, tok

def train_and_eval_optimized(args):
    """Optimized training and evaluation"""
    # Optimize pandas
    optimize_pandas()
    
    # Device setup
    device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f"🖥️  Using device: {device}")
    
    # Set seed
    set_seed(args.seed)
    
    # Load data
    train_loader, val_loader, test_loader, num_labels, tok = make_loaders_optimized(args)
    
    # Initialize model
    print("🤖 Initializing BERT model...")
    model = BertClassifier(args.model_name, num_labels).to(device)
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"📊 Total parameters: {total_params:,}")
    print(f"📊 Trainable parameters: {trainable_params:,}")
    
    # Calculate class weights efficiently
    print("⚖️  Calculating class weights...")
    labels = []
    for batch in train_loader:
        labels.extend(batch['labels'].tolist())
        if len(labels) >= 10000:  # Sample first 10k for speed
            break
    
    cnt = Counter(labels)
    total = sum(cnt.values())
    class_weights = torch.tensor([total/(num_labels*cnt[i]) for i in range(num_labels)], dtype=torch.float32).to(device)
    print(f"✅ Class weights calculated")
    
    # Optimizer and scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    num_training_steps = len(train_loader) * args.epochs
    num_warmup_steps = int(args.warmup_ratio * num_training_steps)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps, num_training_steps)
    loss_fn = nn.CrossEntropyLoss(weight=class_weights)
    
    # Training loop
    print("🎯 Starting training...")
    best_f1, patience = -1.0, 0
    history = []
    
    for epoch in range(1, args.epochs + 1):
        print(f"\n📅 Epoch {epoch}/{args.epochs}")
        
        # Training
        model.train()
        train_losses, train_preds, train_labels = [], [], []
        
        for batch_idx, batch in enumerate(train_loader):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            token_type_ids = batch.get('token_type_ids')
            if token_type_ids is not None: 
                token_type_ids = token_type_ids.to(device)
            labels = batch['labels'].to(device)
            
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
            if batch_idx % 100 == 0:
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
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                token_type_ids = batch.get('token_type_ids')
                if token_type_ids is not None: 
                    token_type_ids = token_type_ids.to(device)
                labels = batch['labels'].to(device)
                
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
        with open(os.path.join(args.out_dir, 'history.json'), 'w') as f: 
            json.dump(history, f, indent=2)
        
        # Early stopping
        if va_f1 > best_f1:
            best_f1 = va_f1
            patience = 0
            torch.save(model.state_dict(), os.path.join(args.out_dir, 'best_model.pt'))
            print(f"💾 New best model saved! F1: {best_f1:.4f}")
        else:
            patience += 1
            if patience >= args.patience:
                print(f"⏹️  Early stopping triggered after {args.patience} epochs")
                break
        
        # Memory cleanup
        gc.collect()
    
    # Final evaluation
    print("\n🧪 Final evaluation on test set...")
    model.load_state_dict(torch.load(os.path.join(args.out_dir, 'best_model.pt'), map_location=device))
    model.to(device)
    model.eval()
    
    test_preds, test_labels = [], []
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            token_type_ids = batch.get('token_type_ids')
            if token_type_ids is not None: 
                token_type_ids = token_type_ids.to(device)
            labels = batch['labels'].to(device)
            
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
    
    with open(os.path.join(args.out_dir, 'final_results.json'), 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to: {args.out_dir}")
    print("🎉 Training complete!")

def parse_args():
    ap = argparse.ArgumentParser(description="Ultra-optimized BERT training for text classification")
    ap.add_argument('--train_path', type=str, required=True, help='Path to training CSV')
    ap.add_argument('--val_path', type=str, required=True, help='Path to validation CSV')
    ap.add_argument('--test_path', type=str, required=True, help='Path to test CSV')
    ap.add_argument('--text_col', type=str, default='cleaned_text', help='Text column name')
    ap.add_argument('--label_col', type=str, default='category', help='Label column name')
    ap.add_argument('--model_name', type=str, default='bert-base-uncased', help='BERT model name')
    ap.add_argument('--max_len', type=int, default=256, help='Maximum sequence length')
    ap.add_argument('--batch_size', type=int, default=16, help='Batch size')
    ap.add_argument('--epochs', type=int, default=4, help='Number of epochs')
    ap.add_argument('--lr', type=float, default=2e-5, help='Learning rate')
    ap.add_argument('--warmup_ratio', type=float, default=0.1, help='Warmup ratio')
    ap.add_argument('--weight_decay', type=float, default=0.01, help='Weight decay')
    ap.add_argument('--patience', type=int, default=3, help='Early stopping patience')
    ap.add_argument('--seed', type=int, default=42, help='Random seed')
    ap.add_argument('--out_dir', type=str, default='bert_output', help='Output directory')
    return ap.parse_args()

if __name__ == "__main__":
    args = parse_args()
    print("🚀 Starting ULTRA-OPTIMIZED BERT Training!")
    print("=" * 60)
    train_and_eval_optimized(args)
