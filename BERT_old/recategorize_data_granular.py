#!/usr/bin/env python3
"""
Granular Data Recategorization Script for Authenticator.ai
Breaks down each main category into individual, specific subcategories
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
OUTPUT_DIR = Path("recategorized_data_granular")

def get_text_column(df):
    """Find the appropriate text column in the dataframe"""
    text_columns = ['cleaned_text', 'text', 'text_content', 'content', 'sentence', 'question', 'answer']
    
    for col in text_columns:
        if col in df.columns:
            return col
    return None

def map_dataset_to_granular_category(file_path):
    """Map dataset path to specific granular category and subcategory"""
    path_str = str(file_path).lower()
    
    # Education - K-12 Administrative
    if "student_records" in path_str:
        return "Education", "student_records"
    elif "transcripts" in path_str:
        return "Education", "transcripts"
    elif "certificates" in path_str:
        return "Education", "certificates"
    elif "report_cards" in path_str:
        return "Education", "report_cards"
    elif "attendance_logs" in path_str:
        return "Education", "attendance_logs"
    elif "forms" in path_str:
        return "Education", "forms"
    elif "transcript_verification" in path_str:
        return "Education", "transcript_verification"
    elif "immunization_records" in path_str:
        return "Education", "immunization_records"
    
    # Education - K-12 Education Content
    elif "science_questions" in path_str:
        return "Education", "science_questions"
    elif "math_qa" in path_str:
        return "Education", "math_qa"
    elif "reading_comprehension" in path_str or "race" in path_str:
        return "Education", "reading_comprehension"
    elif "writing_samples" in path_str:
        return "Education", "writing_samples"
    elif "social_studies" in path_str:
        return "Education", "social_studies"
    elif "ai2_arc" in path_str:
        return "Education", "science_qa"
    elif "gsm8k" in path_str:
        return "Education", "grade_school_math"
    
    # Education - Higher Education
    elif "education" in path_str and ("synthetic" in path_str or "higher" in path_str):
        return "Education", "higher_education"
    
    # Finance - Insurance
    elif "insurance_qa" in path_str:
        return "Finance", "insurance_qa"
    elif "policy_documents" in path_str:
        return "Finance", "policy_documents"
    elif "claim_verification" in path_str:
        return "Finance", "claim_verification"
    elif "insurance" in path_str and "synthetic" in path_str:
        return "Finance", "insurance_general"
    
    # Finance - Banking
    elif "banking" in path_str:
        return "Finance", "banking_documents"
    elif "financial" in path_str:
        return "Finance", "financial_reports"
    
    # Medical
    elif "medical" in path_str:
        return "Medical", "medical_records"
    elif "health" in path_str:
        return "Medical", "health_insurance"
    elif "prescription" in path_str:
        return "Medical", "prescriptions"
    elif "lab_report" in path_str:
        return "Medical", "lab_reports"
    
    # Supply Chain
    elif "procurement" in path_str:
        return "Supply_Chain", "procurement_documents"
    elif "inventory" in path_str:
        return "Supply_Chain", "inventory_records"
    elif "shipping" in path_str:
        return "Supply_Chain", "shipping_documents"
    elif "logistics" in path_str:
        return "Supply_Chain", "logistics_reports"
    
    # Other - Legal
    elif "legal" in path_str and "synthetic" in path_str:
        return "Other", "legal_general"
    elif "contract_verification" in path_str:
        return "Other", "contract_verification"
    elif "court_documents" in path_str:
        return "Other", "court_documents"
    elif "lex_glue" in path_str:
        return "Other", "legal_qa"
    
    # Other - Resume/Employment
    elif "resume" in path_str and "synthetic" in path_str:
        return "Other", "resume_general"
    elif "resume_screening" in path_str:
        return "Other", "resume_screening"
    elif "job_postings" in path_str:
        return "Other", "job_postings"
    elif "employment" in path_str:
        return "Other", "employment_documents"
    
    # Other - Vision Datasets
    elif "vision_datasets" in path_str:
        if "cifar10" in path_str:
            return "Other", "cifar10_images"
        elif "mnist" in path_str:
            return "Other", "mnist_digits"
        elif "fashion_mnist" in path_str:
            return "Other", "fashion_mnist"
        elif "svhn" in path_str:
            return "Other", "street_view_numbers"
        elif "sroie" in path_str:
            return "Other", "receipt_ocr"
        elif "textocr" in path_str:
            return "Other", "text_ocr"
        elif "coco_text" in path_str:
            return "Other", "coco_text_detection"
        elif "total_text" in path_str:
            return "Other", "total_text_detection"
        elif "icdar" in path_str:
            return "Other", "icdar_document_analysis"
        elif "born_digital" in path_str:
            return "Other", "born_digital_images"
        elif "street_view_text" in path_str:
            return "Other", "street_view_text"
        else:
            return "Other", "vision_general"
    
    # Other - Forgery Detection
    elif "forgery_vlm" in path_str:
        if "deepfake_detection" in path_str:
            return "Other", "deepfake_detection"
        elif "signature_forgery" in path_str:
            return "Other", "signature_forgery"
        elif "document_tampering" in path_str:
            return "Other", "document_tampering"
        elif "image_manipulation" in path_str:
            return "Other", "image_manipulation"
        elif "tampering_detection" in path_str:
            return "Other", "tampering_detection"
        elif "manipulation_detection" in path_str:
            return "Other", "manipulation_detection"
        elif "audeering_forgery" in path_str:
            return "Other", "audeering_forgery"
        else:
            return "Other", "forgery_general"
    
    # Other - General Document Classification
    elif "general_document_classification" in path_str:
        if "ag_news" in path_str:
            return "Other", "news_articles"
        elif "imdb" in path_str:
            return "Other", "movie_reviews"
        elif "yelp_polarity" in path_str:
            return "Other", "restaurant_reviews"
        elif "imagefolder_classification" in path_str:
            return "Other", "image_classification"
        elif "cord_receipt" in path_str:
            return "Other", "receipt_documents"
        elif "rvl_cdip" in path_str:
            return "Other", "document_images"
        elif "docformer" in path_str:
            return "Other", "document_understanding"
        elif "crest" in path_str:
            return "Other", "document_analysis"
        elif "infotabs" in path_str:
            return "Other", "table_documents"
        elif "dbpedia_14" in path_str:
            return "Other", "knowledge_base"
        elif "cuad" in path_str:
            return "Other", "contract_understanding"
        elif "bgt" in path_str:
            return "Other", "background_text"
        elif "publaynet" in path_str:
            return "Other", "publication_layout"
        elif "totto" in path_str:
            return "Other", "table_to_text"
        elif "dude" in path_str:
            return "Other", "document_understanding"
        elif "imda" in path_str:
            return "Other", "image_document_analysis"
        elif "docbank" in path_str:
            return "Other", "document_bank"
        elif "doclaynet" in path_str:
            return "Other", "document_layout"
        else:
            return "Other", "general_documents"
    
    # Other - General (fallback)
    else:
        return "Other", "general_documents"

def process_csv_files():
    """Process and recategorize CSV files with granular categories"""
    print("Processing CSV files with granular categories...")
    
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
                
            # Map to granular category
            category, subcategory = map_dataset_to_granular_category(csv_file)
            
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

def main():
    """Main execution function"""
    print("🚀 Starting Granular Data Recategorization...")
    
    # Process CSV files
    combined_data = process_csv_files()
    
    if combined_data is not None:
        print(f"\n✅ Granular recategorization complete!")
        print(f"📊 Total samples: {len(combined_data)}")
        print(f"📁 Output directory: {OUTPUT_DIR}")
        
        # Print final statistics
        print("\n📈 Final Category Distribution:")
        category_counts = combined_data['main_category'].value_counts()
        for category, count in category_counts.items():
            print(f"  {category}: {count:,} samples")
            
        print(f"\n🎯 Total unique subcategories: {len(combined_data['subcategory'].unique())}")
            
    else:
        print("❌ No data found to process!")

if __name__ == "__main__":
    main()
