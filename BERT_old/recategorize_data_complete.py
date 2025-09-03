#!/usr/bin/env python3
"""
Complete Data Recategorization Script for Authenticator.ai
Includes all granular subcategories for all 5 main categories
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
OUTPUT_DIR = Path("recategorized_data_complete")

# Complete category framework
COMPLETE_CATEGORIES = {
    "Education": {
        "description": "Educational documents, academic content, student records",
        "subcategories": {
            # K-12 Administrative
            "student_records": "Student records, enrollment documents",
            "transcripts": "Academic transcripts, grade reports",
            "certificates": "Academic certificates, diplomas",
            "report_cards": "Student report cards, progress reports",
            "attendance_logs": "Attendance records, attendance tracking",
            "forms": "Educational forms, administrative forms",
            "transcript_verification": "Transcript verification documents",
            "immunization_records": "Immunization records, health records",
            
            # K-12 Education Content
            "science_questions": "Science questions, science content",
            "math_qa": "Math Q&A, mathematical problems",
            "reading_comprehension": "Reading comprehension exercises",
            "writing_samples": "Student writing samples, essays",
            "social_studies": "Social studies content, history",
            "science_qa": "Science Q&A (AI2 ARC)",
            "grade_school_math": "Grade school math (GSM8K)",
            
            # Higher Education
            "higher_education": "University documents, research papers",
            "research_papers": "Academic research papers",
            "theses": "Student theses, dissertations",
            "academic_journals": "Academic journal articles",
            "course_materials": "Course materials, syllabi",
            "faculty_records": "Faculty records, professor documents"
        }
    },
    "Finance": {
        "description": "Financial documents, banking, insurance, investments",
        "subcategories": {
            # Insurance
            "insurance_qa": "Insurance Q&A, insurance questions",
            "policy_documents": "Insurance policy documents",
            "claim_verification": "Insurance claim verification",
            "insurance_general": "General insurance documents",
            "health_insurance": "Health insurance documents",
            "auto_insurance": "Automotive insurance documents",
            "life_insurance": "Life insurance documents",
            "property_insurance": "Property insurance documents",
            
            # Banking
            "banking_documents": "Bank statements, banking documents",
            "loan_documents": "Loan applications, loan agreements",
            "credit_reports": "Credit reports, credit history",
            "mortgage_documents": "Mortgage documents, home loans",
            "account_statements": "Account statements, balance sheets",
            
            # Investment
            "investment_documents": "Investment documents, portfolios",
            "stock_reports": "Stock reports, market analysis",
            "mutual_funds": "Mutual fund documents",
            "retirement_accounts": "Retirement account documents",
            "tax_documents": "Tax documents, tax returns",
            
            # Financial Reports
            "financial_reports": "Financial statements, audit reports",
            "balance_sheets": "Balance sheets, financial statements",
            "income_statements": "Income statements, profit/loss",
            "cash_flow_statements": "Cash flow statements",
            "audit_reports": "Audit reports, financial audits"
        }
    },
    "Medical": {
        "description": "Healthcare documents, medical records, health insurance",
        "subcategories": {
            # Medical Records
            "medical_records": "Patient medical records",
            "patient_history": "Patient medical history",
            "diagnostic_reports": "Diagnostic reports, test results",
            "treatment_plans": "Treatment plans, care plans",
            "discharge_summaries": "Discharge summaries",
            "consultation_notes": "Consultation notes, doctor notes",
            
            # Health Insurance
            "health_insurance": "Health insurance claims",
            "medical_policies": "Medical insurance policies",
            "claim_forms": "Medical claim forms",
            "benefit_statements": "Health benefit statements",
            "coverage_documents": "Coverage documents",
            
            # Prescriptions
            "prescriptions": "Prescription documents",
            "medication_records": "Medication records, drug history",
            "pharmacy_records": "Pharmacy records",
            "dosage_instructions": "Dosage instructions",
            
            # Medical Reports
            "lab_reports": "Laboratory reports, test results",
            "imaging_reports": "Imaging reports (X-ray, MRI, CT)",
            "pathology_reports": "Pathology reports",
            "surgical_reports": "Surgical reports, operation notes",
            "emergency_reports": "Emergency room reports",
            
            # Medical Forms
            "consent_forms": "Medical consent forms",
            "intake_forms": "Patient intake forms",
            "referral_forms": "Medical referral forms",
            "insurance_forms": "Medical insurance forms"
        }
    },
    "Supply_Chain": {
        "description": "Logistics, procurement, inventory, shipping documents",
        "subcategories": {
            # Procurement
            "procurement_documents": "Purchase orders, procurement contracts",
            "vendor_contracts": "Vendor contracts, supplier agreements",
            "request_for_proposals": "RFPs, request for proposals",
            "bid_documents": "Bid documents, tender documents",
            "purchase_agreements": "Purchase agreements",
            
            # Inventory
            "inventory_records": "Inventory records, stock records",
            "warehouse_reports": "Warehouse reports, storage records",
            "stock_management": "Stock management documents",
            "inventory_audits": "Inventory audit reports",
            "supply_reports": "Supply reports, material reports",
            
            # Shipping
            "shipping_documents": "Bills of lading, shipping manifests",
            "delivery_receipts": "Delivery receipts, proof of delivery",
            "tracking_documents": "Tracking documents, shipment tracking",
            "customs_documents": "Customs documents, import/export",
            "freight_documents": "Freight documents, cargo documents",
            
            # Logistics
            "logistics_reports": "Logistics reports, supply chain reports",
            "route_plans": "Route planning documents",
            "transportation_contracts": "Transportation contracts",
            "distribution_reports": "Distribution reports",
            "supply_chain_analytics": "Supply chain analytics reports"
        }
    },
    "Other": {
        "description": "General documents, miscellaneous content",
        "subcategories": {
            # Legal
            "legal_general": "General legal documents",
            "contract_verification": "Contract verification",
            "court_documents": "Court documents, legal filings",
            "legal_qa": "Legal Q&A (Lex Glue)",
            "legal_contracts": "Legal contracts, agreements",
            "legal_opinions": "Legal opinions, legal advice",
            "regulatory_documents": "Regulatory documents, compliance",
            
            # Resume/Employment
            "resume_general": "General resume documents",
            "resume_screening": "Resume screening documents",
            "job_postings": "Job postings, job descriptions",
            "employment_documents": "Employment documents",
            "performance_reviews": "Performance reviews",
            "employment_contracts": "Employment contracts",
            
            # Vision Datasets
            "image_classification": "Image classification datasets",
            "cifar10_images": "CIFAR-10 image classification",
            "mnist_digits": "MNIST handwritten digits",
            "fashion_mnist": "Fashion MNIST dataset",
            "street_view_numbers": "Street view house numbers (SVHN)",
            "receipt_ocr": "Receipt OCR (SROIE)",
            "text_ocr": "Text OCR datasets",
            "coco_text_detection": "COCO text detection",
            "total_text_detection": "Total text detection",
            "icdar_document_analysis": "ICDAR document analysis",
            "born_digital_images": "Born digital images",
            "street_view_text": "Street view text detection",
            "vision_general": "General vision datasets",
            
            # Forgery Detection
            "deepfake_detection": "Deepfake detection",
            "signature_forgery": "Signature forgery detection",
            "document_tampering": "Document tampering detection",
            "image_manipulation": "Image manipulation detection",
            "tampering_detection": "Tampering detection",
            "manipulation_detection": "Manipulation detection",
            "audeering_forgery": "Audeering forgery detection",
            "forgery_general": "General forgery detection",
            
            # General Document Classification
            "general_documents": "General document classification",
            "news_articles": "News articles (AG News)",
            "movie_reviews": "Movie reviews (IMDB)",
            "restaurant_reviews": "Restaurant reviews (Yelp)",
            "receipt_documents": "Receipt documents (CORD)",
            "document_images": "Document images (RVL-CDIP)",
            "document_understanding": "Document understanding",
            "document_analysis": "Document analysis (CREST)",
            "table_documents": "Table documents (InfoTabs)",
            "knowledge_base": "Knowledge base (DBPedia)",
            "contract_understanding": "Contract understanding (CUAD)",
            "background_text": "Background text (BGT)",
            "publication_layout": "Publication layout (PubLayNet)",
            "table_to_text": "Table to text (ToTTo)",
            "image_document_analysis": "Image document analysis (IMDA)",
            "document_bank": "Document bank (DocBank)",
            "document_layout": "Document layout (DocLayNet)"
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

def map_dataset_to_complete_category(file_path):
    """Map dataset path to complete granular category and subcategory"""
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
    """Process and recategorize CSV files with complete granular categories"""
    print("Processing CSV files with complete granular categories...")
    
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
                
            # Map to complete granular category
            category, subcategory = map_dataset_to_complete_category(csv_file)
            
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
        
        # Create complete category framework file
        with open(OUTPUT_DIR / "complete_category_framework.json", 'w') as f:
            json.dump(COMPLETE_CATEGORIES, f, indent=2)
        
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

def print_complete_framework():
    """Print the complete category framework"""
    print("\n🎯 COMPLETE CATEGORY FRAMEWORK:")
    print("=" * 50)
    
    for main_category, details in COMPLETE_CATEGORIES.items():
        print(f"\n📁 {main_category}")
        print(f"   Description: {details['description']}")
        print(f"   Subcategories ({len(details['subcategories'])} total):")
        
        for subcategory, description in details['subcategories'].items():
            print(f"     • {subcategory}: {description}")
    
    total_subcategories = sum(len(details['subcategories']) for details in COMPLETE_CATEGORIES.values())
    print(f"\n📊 Total Framework: {len(COMPLETE_CATEGORIES)} main categories, {total_subcategories} subcategories")

def main():
    """Main execution function"""
    print("🚀 Starting Complete Data Recategorization...")
    
    # Print complete framework
    print_complete_framework()
    
    # Process CSV files
    combined_data = process_csv_files()
    
    if combined_data is not None:
        print(f"\n✅ Complete recategorization complete!")
        print(f"📊 Total samples: {len(combined_data)}")
        print(f"📁 Output directory: {OUTPUT_DIR}")
        
        # Print final statistics
        print("\n📈 Final Category Distribution:")
        category_counts = combined_data['main_category'].value_counts()
        for category, count in category_counts.items():
            print(f"  {category}: {count:,} samples")
            
        print(f"\n🎯 Total unique subcategories in data: {len(combined_data['subcategory'].unique())}")
        print(f"🎯 Total subcategories in framework: {sum(len(details['subcategories']) for details in COMPLETE_CATEGORIES.values())}")
            
    else:
        print("❌ No data found to process!")

if __name__ == "__main__":
    main()
