#!/usr/bin/env python3
"""
Fixed Data Recategorization Script for Authenticator.ai
Properly handles different column names and maps data to 5 main categories
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
import shutil

# Configuration
BASE_DIR = Path("../data/training_data")
OUTPUT_DIR = Path("recategorized_data_fixed")
CATEGORIES = {
    "Education": {
        "description": "Educational documents, academic content, student records",
        "subcategories": {
            "k12_administrative": "Student records, transcripts, attendance logs",
            "k12_education": "Academic content, science questions, reading comprehension",
            "higher_education": "University documents, research papers",
            "training_materials": "Corporate training, educational content"
        }
    },
    "Finance": {
        "description": "Financial documents, banking, insurance, investments",
        "subcategories": {
            "insurance_documents": "Insurance claims, policies, verification",
            "banking_documents": "Bank statements, loan documents",
            "investment_documents": "Portfolio reports, investment contracts",
            "financial_reports": "Financial statements, audit reports"
        }
    },
    "Medical": {
        "description": "Healthcare documents, medical records, health insurance",
        "subcategories": {
            "medical_records": "Patient records, medical history",
            "health_insurance": "Health insurance claims, medical policies",
            "prescriptions": "Prescription documents, medication records",
            "medical_reports": "Lab reports, diagnostic reports"
        }
    },
    "Supply_Chain": {
        "description": "Logistics, procurement, inventory, shipping documents",
        "subcategories": {
            "procurement_documents": "Purchase orders, contracts",
            "inventory_records": "Stock records, inventory reports",
            "shipping_documents": "Bills of lading, shipping manifests",
            "logistics_reports": "Supply chain reports, delivery records"
        }
    },
    "Other": {
        "description": "General documents, miscellaneous content",
        "subcategories": {
            "general_documents": "General document classification",
            "news_articles": "News content, articles",
            "legal_documents": "Legal contracts, court documents",
            "resume_employment": "Job postings, resumes",
            "vision_datasets": "Image classification, OCR datasets",
            "forgery_detection": "Document tampering, forgery detection"
        }
    }
}

def get_text_column(df):
    """Find the appropriate text column in the dataframe"""
    text_columns = ['cleaned_text', 'text', 'text_content', 'content', 'sentence', 'question', 'answer']
    
    for col in text_columns:
        if col in df.columns:
            return col
    return None

def get_label_column(df):
    """Find the appropriate label column in the dataframe"""
    label_columns = ['label', 'category', 'class', 'type', 'hierarchical_label']
    
    for col in label_columns:
        if col in df.columns:
            return col
    return None

def map_dataset_to_category(file_path):
    """Map dataset path to category and subcategory"""
    path_str = str(file_path).lower()
    
    # Education
    if "k12_administrative" in path_str:
        return "Education", "k12_administrative"
    elif "k12_education" in path_str:
        return "Education", "k12_education"
    elif "education" in path_str:
        return "Education", "higher_education"
    
    # Finance
    elif "insurance" in path_str:
        return "Finance", "insurance_documents"
    elif "financial" in path_str or "banking" in path_str:
        return "Finance", "banking_documents"
    
    # Medical
    elif "medical" in path_str or "health" in path_str:
        return "Medical", "health_insurance"
    
    # Supply Chain
    elif "logistics" in path_str or "supply" in path_str or "procurement" in path_str:
        return "Supply_Chain", "logistics_reports"
    
    # Other
    elif "legal" in path_str:
        return "Other", "legal_documents"
    elif "resume" in path_str or "employment" in path_str or "job" in path_str:
        return "Other", "resume_employment"
    elif "vision" in path_str or "image" in path_str or "ocr" in path_str:
        return "Other", "vision_datasets"
    elif "forgery" in path_str or "tampering" in path_str or "manipulation" in path_str:
        return "Other", "forgery_detection"
    elif "news" in path_str or "ag_news" in path_str:
        return "Other", "news_articles"
    else:
        return "Other", "general_documents"

def process_csv_files():
    """Process and recategorize CSV files with proper column handling"""
    print("Processing CSV files...")
    
    # Find all CSV files in the training data
    csv_files = list(BASE_DIR.rglob("*.csv"))
    
    all_data = []
    processed_files = 0
    
    for csv_file in csv_files:
        if "manifest" in csv_file.name or "label_map" in csv_file.name or "metadata" in csv_file.name:
            continue
            
        print(f"Processing: {csv_file}")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file, low_memory=False)
            
            if len(df) == 0:
                continue
                
            # Find text column
            text_col = get_text_column(df)
            if text_col is None:
                print(f"  Skipping - no text column found")
                continue
                
            # Map to category
            category, subcategory = map_dataset_to_category(csv_file)
            
            # Create clean dataframe
            df_clean = pd.DataFrame({
                'cleaned_text': df[text_col].astype(str),
                'main_category': category,
                'subcategory': subcategory,
                'hierarchical_label': f"{category}_{subcategory}",
                'source_file': str(csv_file)
            })
            
            # Remove rows with empty or very short text
            df_clean = df_clean[df_clean['cleaned_text'].str.len() > 10]
            df_clean = df_clean.dropna(subset=['cleaned_text'])
            
            if len(df_clean) > 0:
                all_data.append(df_clean)
                processed_files += 1
                print(f"  Added {len(df_clean)} samples -> {category}/{subcategory}")
            
        except Exception as e:
            print(f"  Error processing {csv_file}: {e}")
            continue
    
    if all_data:
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"\nTotal samples: {len(combined_df)}")
        print(f"Processed files: {processed_files}")
        
        # Create train/val/test splits with stratification
        from sklearn.model_selection import train_test_split
        
        # Stratify by main category
        train_df, temp_df = train_test_split(
            combined_df, 
            test_size=0.3, 
            random_state=42, 
            stratify=combined_df['main_category']
        )
        val_df, test_df = train_test_split(
            temp_df, 
            test_size=0.5, 
            random_state=42, 
            stratify=temp_df['main_category']
        )
        
        # Save splits
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        train_df.to_csv(OUTPUT_DIR / "hierarchical_train.csv", index=False)
        val_df.to_csv(OUTPUT_DIR / "hierarchical_val.csv", index=False)
        test_df.to_csv(OUTPUT_DIR / "hierarchical_test.csv", index=False)
        
        # Create label map
        label_map = {}
        unique_labels = combined_df[['main_category', 'subcategory']].drop_duplicates()
        for idx, (_, row) in enumerate(unique_labels.iterrows()):
            label_map[idx] = f"{row['main_category']}_{row['subcategory']}"
        
        with open(OUTPUT_DIR / "hierarchical_label_map.json", 'w') as f:
            json.dump(label_map, f, indent=2)
        
        # Print statistics
        print("\n📊 Data Distribution by Main Category:")
        category_counts = combined_df['main_category'].value_counts()
        for category, count in category_counts.items():
            print(f"  {category}: {count:,} samples")
            
        print("\n📊 Data Distribution by Subcategory:")
        subcategory_counts = combined_df['subcategory'].value_counts()
        for subcategory, count in subcategory_counts.items():
            print(f"  {subcategory}: {count:,} samples")
            
        return combined_df
    else:
        print("No data found!")
        return None

def create_updated_notebook():
    """Create an updated BERT training notebook with the new categorization"""
    notebook_content = '''# BERT Text Classification — Updated Categories

This notebook uses the recategorized data with 5 main categories:
- Education
- Finance  
- Medical
- Supply Chain
- Other

## Config
```python
# ---- Data Loading Mode ----
SINGLE_CSV = False
REAL_ONLY_EVAL = True

# ---- Paths ----
TRAIN_PATH = 'recategorized_data_fixed/hierarchical_train.csv'
VAL_PATH   = 'recategorized_data_fixed/hierarchical_val.csv'
TEST_PATH  = 'recategorized_data_fixed/hierarchical_test.csv'

# ---- Column Names ----
TEXT_COL   = 'cleaned_text'
LABEL_COL  = 'hierarchical_label'
SOURCE_COL = 'source_type'

# ---- Model & Training ----
MODEL_NAME = 'bert-base-uncased'
MAX_LEN = 256
BATCH_SIZE = 16
LR = 2e-5
EPOCHS = 4
WARMUP_RATIO = 0.1
PATIENCE = 3
WEIGHT_DECAY = 0.01
```

## Categories Available:
- **Education**: K12 administrative, educational content, student records
- **Finance**: Insurance documents, banking, financial reports
- **Medical**: Medical records, health insurance, prescriptions
- **Supply Chain**: Procurement, logistics, shipping documents
- **Other**: General documents, legal, resumes, vision datasets, forgery detection
'''
    
    with open("BERT_Training_Updated.ipynb", 'w') as f:
        f.write(notebook_content)

def main():
    """Main execution function"""
    print("🚀 Starting Fixed Data Recategorization...")
    
    # Process CSV files
    combined_data = process_csv_files()
    
    if combined_data is not None:
        print(f"\n✅ Recategorization complete!")
        print(f"📊 Total samples: {len(combined_data)}")
        print(f"📁 Output directory: {OUTPUT_DIR}")
        
        # Create updated notebook
        create_updated_notebook()
        print(f"📓 Updated notebook: BERT_Training_Updated.ipynb")
        
        # Print final statistics
        print("\n📈 Final Category Distribution:")
        category_counts = combined_data['main_category'].value_counts()
        for category, count in category_counts.items():
            print(f"  {category}: {count:,} samples")
            
    else:
        print("❌ No data found to process!")

if __name__ == "__main__":
    main()
