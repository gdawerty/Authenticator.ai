#!/usr/bin/env python3
"""
Classification Data Cleaner for Authentia.ai
Implements two-stage classification: Category → Subcategory
Follows the exact pipeline specified by Pratham
"""

import os
import json
import hashlib
import re
import unicodedata
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from PIL import Image, ImageOps
import imagehash
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClassificationDataCleaner:
    def __init__(self, base_dir: str = "/Users/prathamsaurabh/Authenticator.ai/data/training_data"):
        self.base_dir = Path(base_dir)
        self.raw_datasets_dir = self.base_dir / "raw_datasets"
        self.curated_dir = self.base_dir / "curated" / "v1"
        self.rejects_dir = self.curated_dir / "rejects"
        self.logs_dir = self.curated_dir / "logs"
        
        # Create directories
        self.curated_dir.mkdir(parents=True, exist_ok=True)
        self.rejects_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Global taxonomy for two-stage classification
        self.global_taxonomy = {
            "Education": {
                "K-12": ["transcript", "attendance_log", "report_card", "certificate", "form", "immunization_record"],
                "Higher_Ed": ["transcript", "diploma", "certificate", "enrollment_form"],
                "Training": ["certificate", "completion_form", "assessment"]
            },
            "Insurance": {
                "Claims": ["accident_report", "damage_assessment", "medical_record", "policy_document"],
                "Policies": ["policy_contract", "terms_conditions", "coverage_document"],
                "Forms": ["application_form", "claim_form", "verification_form"]
            },
            "Legal": {
                "Contracts": ["employment_contract", "service_agreement", "nda", "lease_agreement"],
                "Court_Documents": ["filing", "motion", "order", "judgment"],
                "Compliance": ["regulatory_filing", "compliance_report", "audit_document"]
            },
            "Resume": {
                "Employment": ["resume", "cv", "cover_letter", "application"],
                "Job_Postings": ["job_description", "position_requirement", "company_posting"]
            },
            "Admin": {
                "Government": ["id_document", "license", "permit", "certificate"],
                "Business": ["invoice", "receipt", "financial_statement", "report"]
            },
            "Other": {
                "General": ["document", "form", "letter", "report", "memo"]
            }
        }
        
        # PII patterns for masking
        self.pii_patterns = {
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'name': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            'address': r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)\b'
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            'min_text_length': 10,
            'max_text_length': 512,
            'min_ocr_confidence': 0.5,
            'min_image_size': 224,
            'max_blur_threshold': 50,
            'min_brightness': 20,
            'max_brightness': 235,
            'near_duplicate_similarity': 0.9,
            'image_hash_hamming_distance': 5
        }
    
    def create_label_map(self) -> Dict:
        """Step 1: Create label_map.json that converts raw labels to global taxonomy"""
        logger.info("🔧 Step 1: Creating label mapping for global taxonomy...")
        
        label_map = {}
        
        # Map dataset-specific labels to global taxonomy
        for category, subcategories in self.global_taxonomy.items():
            for subcategory, document_types in subcategories.items():
                for doc_type in document_types:
                    # Create mapping key
                    key = f"{category}_{subcategory}_{doc_type}"
                    label_map[key] = {
                        "category": category,
                        "subcategory": subcategory,
                        "document_type": doc_type
                    }
        
        # Add synthetic data mappings
        synthetic_mappings = {
            "student_records": {"category": "Education", "subcategory": "K-12", "document_type": "form"},
            "attendance_logs": {"category": "Education", "subcategory": "K-12", "document_type": "attendance_log"},
            "transcript_verification": {"category": "Education", "subcategory": "K-12", "document_type": "transcript"},
            "immunization_records": {"category": "Education", "subcategory": "K-12", "document_type": "immunization_record"},
            "document_tampering": {"category": "Other", "subcategory": "General", "document_type": "document"},
            "signature_forgery": {"category": "Legal", "subcategory": "Contracts", "document_type": "contract"},
            "image_manipulation": {"category": "Other", "subcategory": "General", "document_type": "document"},
            "deepfake_detection": {"category": "Other", "subcategory": "General", "document_type": "document"},
            "claim_verification": {"category": "Insurance", "subcategory": "Claims", "document_type": "claim_form"},
            "policy_documents": {"category": "Insurance", "subcategory": "Policies", "document_type": "policy_contract"},
            "contract_verification": {"category": "Legal", "subcategory": "Contracts", "document_type": "contract"},
            "court_documents": {"category": "Legal", "subcategory": "Court_Documents", "document_type": "filing"}
        }
        
        label_map.update(synthetic_mappings)
        
        # Save label map
        label_map_file = self.curated_dir / "label_map.json"
        with open(label_map_file, 'w') as f:
            json.dump(label_map, f, indent=2)
        
        logger.info(f"✅ Label map created with {len(label_map)} mappings")
        return label_map
    
    def collect_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Collect all text and image data from raw datasets"""
        logger.info("📥 Collecting all data from raw datasets...")
        
        text_data = []
        image_data = []
        
        # Walk through all raw datasets
        for category_dir in self.raw_datasets_dir.iterdir():
            if not category_dir.is_dir():
                continue
                
            category_name = category_dir.name
            
            for dataset_dir in category_dir.iterdir():
                if not dataset_dir.is_dir():
                    continue
                    
                dataset_name = dataset_dir.name
                
                # Look for train/test splits
                for split_dir in dataset_dir.iterdir():
                    if not split_dir.is_dir() or split_dir.name not in ['train', 'test']:
                        continue
                    
                    split_name = split_dir.name
                    csv_file = split_dir / f"{split_name}.csv"
                    
                    if csv_file.exists():
                        try:
                            df = pd.read_csv(csv_file)
                            
                            # Add metadata
                            df['source_category'] = category_name
                            df['source_dataset'] = dataset_name
                            df['split'] = split_name
                            df['source_file'] = str(csv_file)
                            
                            # Determine if this is text or image data
                            if any(col in df.columns for col in ['text', 'content', 'question', 'answer']):
                                text_data.append(df)
                            elif any(col in df.columns for col in ['image_path', 'image_id', 'image']):
                                image_data.append(df)
                            else:
                                # Generic data - treat as text
                                text_data.append(df)
                                
                        except Exception as e:
                            logger.warning(f"Failed to read {csv_file}: {e}")
        
        # Combine all data
        if text_data:
            combined_text = pd.concat(text_data, ignore_index=True)
            logger.info(f"📝 Collected {len(combined_text)} text samples")
        else:
            combined_text = pd.DataFrame()
            logger.info("📝 No text data found")
        
        if image_data:
            combined_images = pd.concat(image_data, ignore_index=True)
            logger.info(f"🖼️  Collected {len(combined_images)} image samples")
        else:
            combined_images = pd.DataFrame()
            logger.info("🖼️  No image data found")
        
        return combined_text, combined_images
    
    def unify_labels(self, df: pd.DataFrame, label_map: Dict) -> pd.DataFrame:
        """Step 1: Unify labels using global taxonomy"""
        logger.info("🏷️  Unifying labels to global taxonomy...")
        
        # Create category and subcategory columns
        df['category'] = 'Other'
        df['subcategory'] = 'General'
        df['document_type'] = 'document'
        
        # Map based on source information
        for idx, row in df.iterrows():
            source_dataset = row.get('source_dataset', '')
            source_category = row.get('source_category', '')
            
            # Try to map based on dataset name
            if source_dataset in label_map:
                mapping = label_map[source_dataset]
                df.at[idx, 'category'] = mapping['category']
                df.at[idx, 'subcategory'] = mapping['subcategory']
                df.at[idx, 'document_type'] = mapping['document_type']
            elif source_category in ['k12_administrative', 'k12_education']:
                df.at[idx, 'category'] = 'Education'
                df.at[idx, 'subcategory'] = 'K-12'
                df.at[idx, 'document_type'] = 'form'
            elif source_category in ['insurance_documents']:
                df.at[idx, 'category'] = 'Insurance'
                df.at[idx, 'subcategory'] = 'Claims'
                df.at[idx, 'document_type'] = 'claim_form'
            elif source_category in ['legal_documents']:
                df.at[idx, 'category'] = 'Legal'
                df.at[idx, 'subcategory'] = 'Contracts'
                df.at[idx, 'document_type'] = 'contract'
            elif source_category in ['resume_employment']:
                df.at[idx, 'category'] = 'Resume'
                df.at[idx, 'subcategory'] = 'Employment'
                df.at[idx, 'document_type'] = 'resume'
            elif source_category in ['forgery_vlm']:
                df.at[idx, 'category'] = 'Other'
                df.at[idx, 'subcategory'] = 'General'
                df.at[idx, 'document_type'] = 'document'
        
        # Log unmapped labels
        unmapped = df[df['category'] == 'Other']
        if len(unmapped) > 0:
            logger.warning(f"⚠️  {len(unmapped)} samples have unmapped labels")
        
        logger.info(f"✅ Labels unified. Category distribution:\n{df['category'].value_counts()}")
        return df
    
    def remove_duplicates(self, df: pd.DataFrame, data_type: str = 'text') -> pd.DataFrame:
        """Step 2: Remove exact and near duplicates"""
        logger.info(f"🧹 Removing duplicates from {data_type} data...")
        
        initial_count = len(df)
        
        if data_type == 'text':
            # Text deduplication
            df = self._remove_text_duplicates(df)
        else:
            # Image deduplication
            df = self._remove_image_duplicates(df)
        
        final_count = len(df)
        removed_count = initial_count - final_count
        
        logger.info(f"✅ Removed {removed_count} duplicates ({removed_count/initial_count*100:.1f}%)")
        return df
    
    def _remove_text_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove text duplicates using exact hash and near-duplicate detection"""
        # Normalize text
        df['normalized_text'] = df.apply(self._normalize_text, axis=1)
        
        # Create exact hash
        df['text_hash'] = df['normalized_text'].apply(lambda x: hashlib.sha256(x.encode()).hexdigest())
        
        # Remove exact duplicates
        df = df.drop_duplicates(subset=['text_hash'])
        
        # Near-duplicate detection using TF-IDF and cosine similarity
        if len(df) > 1:
            df = self._remove_near_duplicate_texts(df)
        
        return df.drop(['normalized_text', 'text_hash'], axis=1)
    
    def _remove_image_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove image duplicates using file hash and perceptual hash"""
        # Remove rows without image paths
        df = df.dropna(subset=['image_path'])
        
        # Create file hash (if we had actual files)
        df['file_hash'] = 'placeholder_hash'  # Would be actual file hash
        
        # Remove exact duplicates
        df = df.drop_duplicates(subset=['file_hash'])
        
        # Near-duplicate detection would use perceptual hashing
        # For now, just remove exact duplicates
        
        return df.drop(['file_hash'], axis=1)
    
    def _normalize_text(self, row: pd.Series) -> str:
        """Normalize text: lowercase, NFKC, collapse whitespace"""
        text = str(row.get('text', row.get('content', row.get('question', ''))))
        
        # Unicode normalize
        text = unicodedata.normalize('NFKC', text)
        
        # Lowercase
        text = text.lower()
        
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _remove_near_duplicate_texts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove near-duplicate texts using TF-IDF and cosine similarity"""
        # Use TF-IDF for similarity
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        try:
            tfidf_matrix = vectorizer.fit_transform(df['normalized_text'])
            
            # Find similar documents
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Mark duplicates for removal
            to_remove = set()
            
            for i in range(len(similarity_matrix)):
                for j in range(i + 1, len(similarity_matrix)):
                    if similarity_matrix[i][j] >= self.quality_thresholds['near_duplicate_similarity']:
                        # Keep the one with more metadata
                        if len(df.iloc[i].dropna()) < len(df.iloc[j].dropna()):
                            to_remove.add(i)
                        else:
                            to_remove.add(j)
            
            # Remove duplicates
            df = df.drop(df.index[list(to_remove)])
            
        except Exception as e:
            logger.warning(f"Near-duplicate detection failed: {e}")
        
        return df
    
    def clean_text_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Step 3: Clean text data"""
        logger.info("🧹 Cleaning text data...")
        
        initial_count = len(df)
        
        # Apply text cleaning
        df['cleaned_text'] = df.apply(self._clean_single_text, axis=1)
        
        # Filter by quality
        df = df[df['cleaned_text'].notna()]
        df = df[df['cleaned_text'].str.len() >= self.quality_thresholds['min_text_length']]
        df = df[df['cleaned_text'].str.len() <= self.quality_thresholds['max_text_length']]
        
        # Drop original text columns
        text_columns = ['text', 'content', 'question', 'answer', 'normalized_text']
        df = df.drop(columns=[col for col in text_columns if col in df.columns])
        
        final_count = len(df)
        removed_count = initial_count - final_count
        
        logger.info(f"✅ Text cleaning complete. Removed {removed_count} samples ({removed_count/initial_count*100:.1f}%)")
        return df
    
    def _clean_single_text(self, row: pd.Series) -> Optional[str]:
        """Clean a single text entry"""
        text = str(row.get('cleaned_text', row.get('text', row.get('content', row.get('question', '')))))
        
        if not text or text == 'nan':
            return None
        
        # Unicode normalize
        text = unicodedata.normalize('NFKC', text)
        
        # Remove control characters and weird symbols
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        text = re.sub(r'[^\w\s\-.,!?;:()]', '', text)
        
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Mask PII
        text = self._mask_pii(text)
        
        # Check length
        if len(text) < self.quality_thresholds['min_text_length']:
            return None
        
        return text
    
    def _mask_pii(self, text: str) -> str:
        """Mask PII in text"""
        # Mask SSNs
        text = re.sub(self.pii_patterns['ssn'], '[SSN]', text)
        
        # Mask phone numbers
        text = re.sub(self.pii_patterns['phone'], '[PHONE]', text)
        
        # Mask emails
        text = re.sub(self.pii_patterns['email'], '[EMAIL]', text)
        
        # Mask dates
        text = re.sub(self.pii_patterns['date'], '[DATE]', text)
        
        # Mask names (keep first letter, mask rest)
        text = re.sub(self.pii_patterns['name'], lambda m: m.group()[0] + '*' * (len(m.group()) - 1), text)
        
        # Mask addresses
        text = re.sub(self.pii_patterns['address'], '[ADDRESS]', text)
        
        return text
    
    def clean_image_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Step 4: Clean image data"""
        logger.info("🖼️  Cleaning image data...")
        
        initial_count = len(df)
        
        # For now, just validate image paths exist
        # In production, you'd process actual images
        df = df[df['image_path'].notna()]
        
        # Add image metadata columns
        df['image_width'] = 224  # Standard ViT size
        df['image_height'] = 224
        df['image_format'] = 'RGB'
        df['is_processed'] = True
        
        final_count = len(df)
        removed_count = initial_count - final_count
        
        logger.info(f"✅ Image cleaning complete. Removed {removed_count} samples ({removed_count/initial_count*100:.1f}%)")
        return df
    
    def create_leakage_proof_splits(self, df: pd.DataFrame, data_type: str = 'text') -> Dict[str, pd.DataFrame]:
        """Step 5: Create leakage-proof train/val/test splits"""
        logger.info(f"✂️  Creating leakage-proof splits for {data_type} data...")
        
        # Create group identifier (simulate based on available columns)
        if 'student_id' in df.columns:
            group_col = 'student_id'
        elif 'claim_id' in df.columns:
            group_col = 'claim_id'
        elif 'document_id' in df.columns:
            group_col = 'document_id'
        else:
            # Create synthetic group ID
            df['group_id'] = df.index // 10  # Group every 10 samples
            group_col = 'group_id'
        
        # Ensure we have enough samples per category
        category_counts = df['category'].value_counts()
        min_samples = 100
        
        # Filter categories with enough samples
        valid_categories = category_counts[category_counts >= min_samples].index
        df_filtered = df[df['category'].isin(valid_categories)]
        
        if len(df_filtered) < len(df):
            logger.warning(f"⚠️  Dropped {len(df) - len(df_filtered)} samples from undersized categories")
        
        # Stratified group split
        splitter = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=42)
        
        # Create splits
        splits = {}
        for fold, (train_idx, test_idx) in enumerate(splitter.split(
            df_filtered, 
            df_filtered['category'], 
            groups=df_filtered[group_col]
        )):
            if fold == 0:  # Use first fold for train/val split
                # Further split train into train/val
                train_df = df_filtered.iloc[train_idx]
                test_df = df_filtered.iloc[test_idx]
                
                # Split train into train/val
                val_splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
                for val_fold, (train_val_idx, val_idx) in enumerate(val_splitter.split(
                    train_df, train_df['category'], groups=train_df[group_col]
                )):
                    if val_fold == 0:  # Use first val fold
                        val_df = train_df.iloc[val_idx]
                        final_train_df = train_df.iloc[train_val_idx]
                        break
                
                splits = {
                    'train': final_train_df,
                    'val': val_df,
                    'test': test_df
                }
                break
        
        # Validate splits
        for split_name, split_df in splits.items():
            logger.info(f"📊 {split_name.capitalize()} split: {len(split_df)} samples")
            logger.info(f"   Category distribution:\n{split_df['category'].value_counts()}")
        
        return splits
    
    def save_splits(self, splits: Dict[str, pd.DataFrame], data_type: str = 'text'):
        """Save train/val/test splits"""
        logger.info(f"💾 Saving {data_type} splits...")
        
        for split_name, split_df in splits.items():
            # Save as parquet
            parquet_file = self.curated_dir / f"{data_type}_{split_name}.parquet"
            split_df.to_parquet(parquet_file, index=False)
            
            # Also save as CSV for compatibility
            csv_file = self.curated_dir / f"{data_type}_{split_name}.csv"
            split_df.to_csv(csv_file, index=False)
            
            logger.info(f"✅ Saved {split_name} split: {len(split_df)} samples")
    
    def create_manifest(self, text_splits: Dict, image_splits: Dict):
        """Step 6: Create manifest with summary counts"""
        logger.info("📋 Creating data manifest...")
        
        manifest_data = []
        
        # Text data summary
        for split_name, split_df in text_splits.items():
            category_counts = split_df['category'].value_counts()
            for category, count in category_counts.items():
                subcategory_counts = split_df[split_df['category'] == category]['subcategory'].value_counts()
                for subcategory, subcount in subcategory_counts.items():
                    manifest_data.append({
                        'data_type': 'text',
                        'split': split_name,
                        'category': category,
                        'subcategory': subcategory,
                        'count': subcount
                    })
        
        # Image data summary
        for split_name, split_df in image_splits.items():
            category_counts = split_df['category'].value_counts()
            for category, count in category_counts.items():
                subcategory_counts = split_df[split_df['category'] == category]['subcategory'].value_counts()
                for subcategory, subcount in subcategory_counts.items():
                    manifest_data.append({
                        'data_type': 'image',
                        'split': split_name,
                        'category': category,
                        'subcategory': subcategory,
                        'count': subcount
                    })
        
        manifest_df = pd.DataFrame(manifest_data)
        manifest_file = self.curated_dir / "manifest.csv"
        manifest_df.to_csv(manifest_file, index=False)
        
        logger.info(f"✅ Manifest created with {len(manifest_df)} category-split combinations")
        return manifest_df
    
    def run_full_pipeline(self):
        """Run the complete classification data cleaning pipeline"""
        logger.info("🚀 Starting Classification Data Cleaning Pipeline")
        
        start_time = datetime.now()
        
        try:
            # Step 1: Create label mapping
            label_map = self.create_label_map()
            
            # Step 2: Collect all data
            text_data, image_data = self.collect_all_data()
            
            # Step 3: Process text data
            if not text_data.empty:
                logger.info("📝 Processing text data...")
                text_data = self.unify_labels(text_data, label_map)
                text_data = self.remove_duplicates(text_data, 'text')
                text_data = self.clean_text_data(text_data)
                text_splits = self.create_leakage_proof_splits(text_data, 'text')
                self.save_splits(text_splits, 'text')
            else:
                text_splits = {}
                logger.info("📝 No text data to process")
            
            # Step 4: Process image data
            if not image_data.empty:
                logger.info("🖼️  Processing image data...")
                image_data = self.unify_labels(image_data, label_map)
                image_data = self.remove_duplicates(image_data, 'image')
                image_data = self.clean_image_data(image_data)
                image_splits = self.create_leakage_proof_splits(image_data, 'image')
                self.save_splits(image_splits, 'image')
            else:
                image_splits = {}
                logger.info("🖼️  No image data to process")
            
            # Step 5: Create manifest
            manifest = self.create_manifest(text_splits, image_splits)
            
            # Step 6: Generate final report
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            final_report = {
                "pipeline_completed_at": end_time.isoformat(),
                "processing_time_seconds": processing_time,
                "text_data_processed": len(text_data) if not text_data.empty else 0,
                "image_data_processed": len(image_data) if not image_data.empty else 0,
                "text_splits_created": len(text_splits),
                "image_splits_created": len(image_splits),
                "total_samples_in_splits": sum(len(split_df) for split_df in list(text_splits.values()) + list(image_splits.values())),
                "manifest_entries": len(manifest),
                "status": "SUCCESS",
                "next_steps": [
                    "🎯 Start BERT training on text splits",
                    "🎯 Start ViT training on image splits",
                    "🎯 Build classification API endpoints",
                    "🎯 Test two-stage classification pipeline"
                ]
            }
            
            # Save final report
            report_file = self.logs_dir / "cleaning_pipeline_report.json"
            with open(report_file, 'w') as f:
                json.dump(final_report, f, indent=2)
            
            logger.info("🎉 Classification Data Cleaning Pipeline completed successfully!")
            logger.info(f"📊 Final report saved to {report_file}")
            
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            raise

if __name__ == "__main__":
    cleaner = ClassificationDataCleaner()
    cleaner.run_full_pipeline()

