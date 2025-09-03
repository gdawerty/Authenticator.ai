"""
Data Processor for BERT Training
Handles CSV data loading, preprocessing, and dataset creation
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
import torch
from transformers import AutoTokenizer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentDataset(Dataset):
    """Custom Dataset for document classification"""
    
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        # Tokenize text
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class DataProcessor:
    """Handles data loading and preprocessing"""
    
    def __init__(self, config):
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)
        self.label_encoder = LabelEncoder()
        
    def load_data(self):
        """Load and preprocess CSV data"""
        logger.info("📥 Loading data from CSV files...")
        
        # Load CSV files
        train_df = pd.read_csv(self.config.TRAIN_FILE)
        val_df = pd.read_csv(self.config.VAL_FILE)
        test_df = pd.read_csv(self.config.TEST_FILE)
        
        logger.info(f"📊 Loaded {len(train_df)} training, {len(val_df)} validation, {len(test_df)} test samples")
        
        # Extract text and labels
        train_texts = train_df['cleaned_text'].fillna('').astype(str)
        val_texts = val_df['cleaned_text'].fillna('').astype(str)
        test_texts = test_df['cleaned_text'].fillna('').astype(str)
        
        # Encode labels
        all_categories = train_df['category'].tolist() + val_df['category'].tolist() + test_df['category'].tolist()
        self.label_encoder.fit(all_categories)
        
        train_labels = self.label_encoder.transform(train_df['category'])
        val_labels = self.label_encoder.transform(val_df['category'])
        test_labels = self.label_encoder.transform(test_df['category'])
        
        logger.info(f"🏷️  Encoded {len(self.label_encoder.classes_)} categories: {self.label_encoder.classes_}")
        
        # Create datasets
        train_dataset = DocumentDataset(train_texts, train_labels, self.tokenizer, self.config.MAX_LENGTH)
        val_dataset = DocumentDataset(val_texts, val_labels, self.tokenizer, self.config.MAX_LENGTH)
        test_dataset = DocumentDataset(test_texts, test_labels, self.tokenizer, self.config.MAX_LENGTH)
        
        # Create dataloaders
        train_loader = DataLoader(
            train_dataset, 
            batch_size=self.config.BATCH_SIZE, 
            shuffle=True,
            num_workers=2
        )
        
        val_loader = DataLoader(
            val_dataset, 
            batch_size=self.config.BATCH_SIZE, 
            shuffle=False,
            num_workers=2
        )
        
        test_loader = DataLoader(
            test_dataset, 
            batch_size=self.config.BATCH_SIZE, 
            shuffle=False,
            num_workers=2
        )
        
        logger.info("✅ Data loading complete!")
        
        return train_loader, val_loader, test_loader
    
    def get_label_mapping(self):
        """Get mapping between encoded labels and category names"""
        return {i: label for i, label in enumerate(self.label_encoder.classes_)}
    
    def get_num_classes(self):
        """Get number of unique categories"""
        return len(self.label_encoder.classes_)
