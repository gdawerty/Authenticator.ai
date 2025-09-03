#!/usr/bin/env python3
"""
Data Recategorization Script for Authenticator.ai
Recategorizes all training data into 5 main categories with proper subcategories
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
OUTPUT_DIR = Path("recategorized_data")
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

def create_directory_structure():
    """Create the new directory structure for recategorized data"""
    print("Creating directory structure...")
    
    for category in CATEGORIES.keys():
        category_dir = OUTPUT_DIR / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        for subcategory in CATEGORIES[category]["subcategories"].keys():
            subcategory_dir = category_dir / subcategory
            subcategory_dir.mkdir(exist_ok=True)
            
            # Create train/val/test subdirectories
            for split in ["train", "val", "test"]:
                (subcategory_dir / split).mkdir(exist_ok=True)

def map_datasets_to_categories():
    """Map existing datasets to new categories"""
    dataset_mapping = {
        # Education
        "k12_administrative": ("Education", "k12_administrative"),
        "k12_education": ("Education", "k12_education"),
        "education_documents": ("Education", "higher_education"),
        
        # Finance
        "insurance_documents": ("Finance", "insurance_documents"),
        
        # Medical (will be mapped from insurance and health-related data)
        "health_insurance": ("Medical", "health_insurance"),
        
        # Supply Chain (will be mapped from logistics-related data)
        "logistics_documents": ("Supply_Chain", "logistics_reports"),
        
        # Other
        "general_document_classification": ("Other", "general_documents"),
        "legal_documents": ("Other", "legal_documents"),
        "resume_employment": ("Other", "resume_employment"),
        "vision_datasets": ("Other", "vision_datasets"),
        "forgery_vlm": ("Other", "forgery_detection")
    }
    
    return dataset_mapping

def process_csv_files():
    """Process and recategorize CSV files"""
    print("Processing CSV files...")
    
    # Find all CSV files in the training data
    csv_files = list(BASE_DIR.rglob("*.csv"))
    
    all_data = []
    dataset_mapping = map_datasets_to_categories()
    
    for csv_file in csv_files:
        if "manifest" in csv_file.name or "label_map" in csv_file.name:
            continue
            
        print(f"Processing: {csv_file}")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file, low_memory=False)
            
            # Determine category based on file path
            relative_path = csv_file.relative_to(BASE_DIR)
            path_parts = relative_path.parts
            
            # Map to new category
            if "k12_administrative" in path_parts:
                category, subcategory = "Education", "k12_administrative"
            elif "k12_education" in path_parts:
                category, subcategory = "Education", "k12_education"
            elif "education_documents" in path_parts:
                category, subcategory = "Education", "higher_education"
            elif "insurance_documents" in path_parts:
                category, subcategory = "Finance", "insurance_documents"
            elif "legal_documents" in path_parts:
                category, subcategory = "Other", "legal_documents"
            elif "resume_employment" in path_parts:
                category, subcategory = "Other", "resume_employment"
            elif "vision_datasets" in path_parts:
                category, subcategory = "Other", "vision_datasets"
            elif "forgery_vlm" in path_parts:
                category, subcategory = "Other", "forgery_detection"
            elif "general_document_classification" in path_parts:
                category, subcategory = "Other", "general_documents"
            else:
                category, subcategory = "Other", "general_documents"
            
            # Add category information
            df['main_category'] = category
            df['subcategory'] = subcategory
            df['hierarchical_label'] = f"{category}_{subcategory}"
            
            # Ensure we have the required columns
            if 'cleaned_text' not in df.columns and 'text' in df.columns:
                df['cleaned_text'] = df['text']
            elif 'cleaned_text' not in df.columns and 'text_content' in df.columns:
                df['cleaned_text'] = df['text_content']
            
            # Select relevant columns
            columns_to_keep = ['cleaned_text', 'main_category', 'subcategory', 'hierarchical_label']
            available_columns = [col for col in columns_to_keep if col in df.columns]
            
            df_clean = df[available_columns].copy()
            df_clean = df_clean.dropna(subset=['cleaned_text'])
            
            all_data.append(df_clean)
            
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
            continue
    
    if all_data:
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"Total samples: {len(combined_df)}")
        
        # Create train/val/test splits
        train_df, temp_df = train_test_split(combined_df, test_size=0.3, random_state=42, stratify=combined_df['main_category'])
        val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['main_category'])
        
        # Save splits
        train_df.to_csv(OUTPUT_DIR / "hierarchical_train.csv", index=False)
        val_df.to_csv(OUTPUT_DIR / "hierarchical_val.csv", index=False)
        test_df.to_csv(OUTPUT_DIR / "hierarchical_test.csv", index=False)
        
        # Create label map
        label_map = {}
        for idx, (category, subcategory) in enumerate(combined_df[['main_category', 'subcategory']].drop_duplicates().values):
            label_map[idx] = f"{category}_{subcategory}"
        
        with open(OUTPUT_DIR / "hierarchical_label_map.json", 'w') as f:
            json.dump(label_map, f, indent=2)
        
        # Print statistics
        print("\nData Distribution:")
        print(combined_df['main_category'].value_counts())
        print("\nSubcategory Distribution:")
        print(combined_df['subcategory'].value_counts())
        
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
TRAIN_PATH = 'recategorized_data/hierarchical_train.csv'
VAL_PATH   = 'recategorized_data/hierarchical_val.csv'
TEST_PATH  = 'recategorized_data/hierarchical_test.csv'

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
    print("🚀 Starting Data Recategorization...")
    
    # Create directory structure
    create_directory_structure()
    
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
    from sklearn.model_selection import train_test_split
    main()
