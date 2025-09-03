#!/usr/bin/env python3
import os
import json
import argparse
from collections import Counter

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
# Utilities
# ---------------------------
def set_seed(seed: int):
    import random
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)

class TextDataset(Dataset):
    def __init__(self, df, tokenizer, max_len=256):
        self.df = df.reset_index(drop=True)
        self.tok = tokenizer
        self.max_len = max_len
    def __len__(self): return len(self.df)
    def __getitem__(self, i):
        row = self.df.iloc[i]
        enc = self.tok(str(row['text']), truncation=True, padding='max_length', max_length=self.max_len, return_tensors='pt')
        item = {k: v.squeeze(0) for k,v in enc.items()}
        item['labels'] = torch.tensor(int(row['label']), dtype=torch.long)
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
        if labels is not None: return logits, labels
        return logits

def standardize_columns(df, text_col, label_col, source_col):
    out = pd.DataFrame({
        'text': df[text_col].astype(str),
        'label_raw': df[label_col].astype(str),
    })
    if source_col in df.columns:
        out['source_type'] = df[source_col].astype(str)
    else:
        out['source_type'] = 'real'
    return out

def make_loaders(args):
    # Load data (single CSV or 3 files)
    if args.single_csv:
        base = pd.read_csv(args.data_path)
        base = standardize_columns(base, args.text_col, args.label_col, args.source_col)
        # label encoding
        le = LabelEncoder()
        base['label'] = le.fit_transform(base['label_raw'])
        os.makedirs(args.out_dir, exist_ok=True)
        with open(os.path.join(args.out_dir, 'label_map.json'), 'w') as f:
            json.dump({int(i): c for i, c in enumerate(le.classes_)}, f, indent=2)
        if args.real_only_eval:
            real = base[base['source_type'] == 'real']
            rest = base
            real_train, real_holdout = train_test_split(real, test_size=0.20, random_state=args.seed, stratify=real['label'])
            val_df, test_df = train_test_split(real_holdout, test_size=0.50, random_state=args.seed, stratify=real_holdout['label'])
            used_idx = set(pd.concat([val_df, test_df]).index)
            train_df = rest[~rest.index.isin(used_idx)].copy()
        else:
            train_df, holdout = train_test_split(base, test_size=0.20, random_state=args.seed, stratify=base['label'])
            val_df, test_df = train_test_split(holdout, test_size=0.50, random_state=args.seed, stratify=holdout['label'])
    else:
        tr = pd.read_csv(args.train_path); va = pd.read_csv(args.val_path); te = pd.read_csv(args.test_path)
        train_df = standardize_columns(tr, args.text_col, args.label_col, args.source_col)
        val_df   = standardize_columns(va, args.text_col, args.label_col, args.source_col)
        test_df  = standardize_columns(te, args.text_col, args.label_col, args.source_col)
        le = LabelEncoder()
        train_df['label'] = le.fit_transform(train_df['label_raw'])
        val_df['label']   = le.transform(val_df['label_raw'])
        test_df['label']  = le.transform(test_df['label_raw'])
        os.makedirs(args.out_dir, exist_ok=True)
        with open(os.path.join(args.out_dir, 'label_map.json'), 'w') as f:
            json.dump({int(i): c for i, c in enumerate(le.classes_)}, f, indent=2)

    num_labels = len(set(train_df['label']))

    tok = AutoTokenizer.from_pretrained(args.model_name)
    train_ds = TextDataset(train_df, tok, args.max_len)
    val_ds   = TextDataset(val_df, tok, args.max_len)
    test_ds  = TextDataset(test_df, tok, args.max_len)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader   = DataLoader(val_ds, batch_size=args.batch_size)
    test_loader  = DataLoader(test_ds, batch_size=args.batch_size)
    return train_loader, val_loader, test_loader, num_labels, tok

def train_and_eval(args):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    set_seed(args.seed)

    train_loader, val_loader, test_loader, num_labels, tok = make_loaders(args)

    model = BertClassifier(args.model_name, num_labels).to(device)

    # class weights
    labels = []
    for b in train_loader:
        labels.extend(b['labels'].tolist())
    cnt = Counter(labels); total = sum(cnt.values())
    class_weights = torch.tensor([total/(num_labels*cnt[i]) for i in range(num_labels)], dtype=torch.float32).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    num_training_steps = len(train_loader) * args.epochs
    num_warmup_steps = int(args.warmup_ratio * num_training_steps)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps, num_training_steps)
    loss_fn = nn.CrossEntropyLoss(weight=class_weights)

    best_f1, patience = -1.0, 0
    history = []

    for epoch in range(1, args.epochs+1):
        # train
        model.train()
        train_losses, train_preds, train_labels = [], [], []
        for batch in train_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            token_type_ids = batch.get('token_type_ids')
            if token_type_ids is not None: token_type_ids = token_type_ids.to(device)
            labels = batch['labels'].to(device)
            optimizer.zero_grad()
            logits, _ = model(input_ids, attention_mask, token_type_ids, labels)
            loss = loss_fn(logits, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step(); scheduler.step()
            train_losses.append(loss.item())
            train_preds.extend(logits.argmax(-1).detach().cpu().numpy())
            train_labels.extend(labels.detach().cpu().numpy())

        tr_acc = accuracy_score(train_labels, train_preds)
        tr_f1  = f1_score(train_labels, train_preds, average='macro')

        # validate
        model.eval()
        val_losses, val_preds, val_labels = [], [], []
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                token_type_ids = batch.get('token_type_ids')
                if token_type_ids is not None: token_type_ids = token_type_ids.to(device)
                labels = batch['labels'].to(device)
                logits, _ = model(input_ids, attention_mask, token_type_ids, labels)
                loss = loss_fn(logits, labels)
                val_losses.append(loss.item())
                val_preds.extend(logits.argmax(-1).detach().cpu().numpy())
                val_labels.extend(labels.detach().cpu().numpy())

        va_acc = accuracy_score(val_labels, val_preds)
        va_f1  = f1_score(val_labels, val_preds, average='macro')

        print(f"Epoch {epoch}: train_loss={np.mean(train_losses):.4f} val_loss={np.mean(val_losses):.4f} | train_f1={tr_f1:.4f} val_f1={va_f1:.4f}")

        history.append({'epoch': epoch, 'train_loss': float(np.mean(train_losses)), 'val_loss': float(np.mean(val_losses)),
                        'train_acc': float(tr_acc), 'val_acc': float(va_acc), 'train_f1': float(tr_f1), 'val_f1': float(va_f1)})
        os.makedirs(args.out_dir, exist_ok=True)
        with open(os.path.join(args.out_dir, 'history.json'), 'w') as f: json.dump(history, f, indent=2)

        if va_f1 > best_f1:
            best_f1, patience = va_f1, 0
            torch.save(model.state_dict(), os.path.join(args.out_dir, 'best_model.pt'))
        else:
            patience += 1
            if patience >= args.patience:
                print("Early stopping triggered.")
                break

    # test
    model.load_state_dict(torch.load(os.path.join(args.out_dir, 'best_model.pt'), map_location=device))
    model.to(device); model.eval()
    test_preds, test_labels = [], []
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            token_type_ids = batch.get('token_type_ids')
            if token_type_ids is not None: token_type_ids = token_type_ids.to(device)
            labels = batch['labels'].to(device)
            logits, _ = model(input_ids, attention_mask, token_type_ids, labels)
            test_preds.extend(logits.argmax(-1).detach().cpu().numpy())
            test_labels.extend(labels.detach().cpu().numpy())

    acc = accuracy_score(test_labels, test_preds)
    f1m = f1_score(test_labels, test_preds, average='macro')
    print({'test_accuracy': acc, 'test_f1_macro': f1m})
    print("\nPer-class report:\n")
    print(classification_report(test_labels, test_preds, digits=4))

def parse_args():
    ap = argparse.ArgumentParser(description="Train BERT for text classification (self-contained).")
    ap.add_argument('--single_csv', action='store_true', help='Use single CSV and split')
    ap.add_argument('--data_path', type=str, default='data.csv', help='Path to single CSV')
    ap.add_argument('--train_path', type=str, default='train.csv')
    ap.add_argument('--val_path', type=str, default='val.csv')
    ap.add_argument('--test_path', type=str, default='test.csv')
    ap.add_argument('--text_col', type=str, default='text')
    ap.add_argument('--label_col', type=str, default='label')
    ap.add_argument('--source_col', type=str, default='source_type')
    ap.add_argument('--real_only_eval', action='store_true', help='Use real-only val/test (single_csv mode)')
    ap.add_argument('--model_name', type=str, default='bert-base-uncased')
    ap.add_argument('--max_len', type=int, default=256)
    ap.add_argument('--batch_size', type=int, default=16)
    ap.add_argument('--epochs', type=int, default=4)
    ap.add_argument('--lr', type=float, default=2e-5)
    ap.add_argument('--warmup_ratio', type=float, default=0.1)
    ap.add_argument('--weight_decay', type=float, default=0.01)
    ap.add_argument('--patience', type=int, default=3)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--out_dir', type=str, default='bert_out')
    return ap.parse_args()

if __name__ == "__main__":
    args = parse_args()
    train_and_eval(args)
