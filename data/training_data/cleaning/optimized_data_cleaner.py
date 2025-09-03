#!/usr/bin/env python3
"""
Optimized Data Cleaner for Authentia.ai Sprint 2
Leverages M4 Pro's 10 cores for parallel processing
Expected runtime: 15-30 minutes for 1.6M+ samples
"""

import os
import sys
import json
import hashlib
import logging
import multiprocessing as mp
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import StratifiedGroupKFold
import imagehash
from PIL import Image, ImageFilter
import re
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleaning_pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class OptimizedDataCleaner:
    def __init__(self, base_dir: str = "raw_datasets", output_dir: str = "curated/v1"):
        self.base_dir = Path(base_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Use all available cores (M4 Pro = 10 cores)
        self.n_cores = min(10, mp.cpu_count())
        logger.info(f"🚀 Using {self.n_cores} cores for parallel processing")
        
        # Global taxonomy
        self.global_taxonomy = {
            'Education': ['transcript', 'report_card', 'certificate', 'diploma', 'assignment', 'test_paper'],
            'Insurance': ['claim_form', 'policy_document', 'damage_assessment', 'medical_record', 'accident_report'],
            'Legal': ['contract', 'legal_document', 'court_filing', 'agreement', 'legal_brief'],
            'Resume': ['resume', 'cv', 'cover_letter', 'job_application'],
            'Admin': ['form', 'application', 'permit', 'license', 'certificate'],
            'Other': ['general', 'unknown', 'miscellaneous']
        }
        
        # PII patterns
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            'address': r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct)\b',
            'name': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        }
        
        # Quality thresholds - adjusted for synthetic data
        self.quality_thresholds = {
            'min_text_length': 3,  # Reduced from 10 to handle synthetic data
            'max_text_length': 512,
            'min_image_size': 224,
            'max_blur_threshold': 50,
            'min_brightness': 20,
            'max_brightness': 235
        }

    def create_label_mapping(self) -> Dict:
        """Create mapping from dataset names to global taxonomy"""
        logger.info("🔧 Creating label mapping for global taxonomy...")
        
        label_map = {}
        dataset_dirs = list(self.base_dir.rglob("*/dataset_dict.json"))
        
        for dataset_file in dataset_dirs:
            try:
                with open(dataset_file, 'r') as f:
                    dataset_info = json.load(f)
                
                dataset_path = dataset_file.parent
                dataset_name = dataset_path.name
                
                # Map based on path structure
                if 'education' in str(dataset_path).lower():
                    category = 'Education'
                    subcategory = 'transcript' if 'transcript' in str(dataset_path).lower() else 'general'
                elif 'insurance' in str(dataset_path).lower():
                    category = 'Insurance'
                    subcategory = 'claim_form' if 'claim' in str(dataset_path).lower() else 'policy_document'
                elif 'legal' in str(dataset_path).lower():
                    category = 'Legal'
                    subcategory = 'contract' if 'contract' in str(dataset_path).lower() else 'legal_document'
                elif 'resume' in str(dataset_path).lower() or 'employment' in str(dataset_path).lower():
                    category = 'Resume'
                    subcategory = 'resume'
                elif 'admin' in str(dataset_path).lower() or 'form' in str(dataset_path).lower():
                    category = 'Admin'
                    subcategory = 'form'
                else:
                    category = 'Other'
                    subcategory = 'general'
                
                label_map[dataset_name] = {
                    'category': category,
                    'subcategory': subcategory,
                    'document_type': 'document'
                }
                
            except Exception as e:
                logger.warning(f"⚠️  Could not process {dataset_file}: {e}")
                continue
        
        # Save label map
        with open(self.output_dir / 'label_map.json', 'w') as f:
            json.dump(label_map, f, indent=2)
        
        logger.info(f"✅ Label map created with {len(label_map)} mappings")
        return label_map

    def collect_data_parallel(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Collect all data using parallel processing"""
        logger.info("📥 Collecting all data from raw datasets...")
        
        # Collect text data
        text_data = []
        image_data = []
        
        # Find all CSV files
        csv_files = list(self.base_dir.rglob("*.csv"))
        logger.info(f"🔍 Found {len(csv_files)} CSV files to process")
        
        def process_csv_file(csv_file):
            try:
                df = pd.read_csv(csv_file, low_memory=False)
                source_dataset = csv_file.parent.name
                
                # Add source information
                df['source_dataset'] = source_dataset
                df['source_path'] = str(csv_file)
                
                # Determine source type (synthetic vs real)
                if any(keyword in source_dataset.lower() for keyword in ['synthetic', 'generated', 'fake', 'artificial']):
                    df['source_type'] = 'synthetic'
                else:
                    df['source_type'] = 'real'
                
                # Determine if it's text or image data based on columns
                if 'text_content' in df.columns or 'text' in df.columns:
                    # Text dataset
                    return ('text', df)
                elif 'image_path' in df.columns or 'image' in df.columns:
                    # Image dataset
                    return ('image', df)
                elif 'label' in df.columns and len(df.columns) <= 3:
                    # Simple labeled dataset (likely image)
                    return ('image', df)
                else:
                    # Unknown format, try to infer
                    if len(df.columns) <= 5:
                        return ('text', df)
                    else:
                        return ('unknown', df)
                    
            except Exception as e:
                logger.warning(f"⚠️  Could not read {csv_file}: {e}")
                return (None, None)
        
        # Process CSV files in parallel
        with ThreadPoolExecutor(max_workers=self.n_cores) as executor:
            futures = [executor.submit(process_csv_file, csv_file) for csv_file in csv_files]
            
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing CSV files"):
                result = future.result()
                if result and result[0] == 'text':
                    text_data.append(result[1])
                elif result and result[0] == 'image':
                    image_data.append(result[1])
        
        # Combine text data
        if text_data:
            text_df = pd.concat(text_data, ignore_index=True)
            logger.info(f"📝 Collected {len(text_df)} text samples")
        else:
            text_df = pd.DataFrame()
            logger.info("📝 No text data found")
        
        # Combine image data
        if image_data:
            image_df = pd.concat(image_data, ignore_index=True)
            logger.info(f"🖼️  Collected {len(image_df)} image samples")
        else:
            image_df = pd.DataFrame()
            logger.info("🖼️  No image data found")
        
        return text_df, image_df

    def clean_text_parallel(self, df: pd.DataFrame, label_map: Dict) -> pd.DataFrame:
        """Clean text data using parallel processing"""
        logger.info("🧹 Cleaning text data...")
        
        if df.empty:
            return df
        
        # Apply label mapping in parallel
        def apply_labels(row):
            source_dataset = row.get('source_dataset', '')
            if source_dataset in label_map:
                mapping = label_map[source_dataset]
                return pd.Series({
                    'category': mapping['category'],
                    'subcategory': mapping['subcategory'],
                    'document_type': mapping['document_type']
                })
            else:
                return pd.Series({
                    'category': 'Other',
                    'subcategory': 'general',
                    'document_type': 'document'
                })
        
        # Apply labels
        label_results = df.apply(apply_labels, axis=1)
        df = pd.concat([df, label_results], axis=1)
        
        # Determine text column to use
        text_column = None
        if 'text_content' in df.columns:
            text_column = 'text_content'
        elif 'text' in df.columns:
            text_column = 'text'
        else:
            logger.warning("⚠️  No text column found, skipping text cleaning")
            return df
        
        logger.info(f"🔍 Using text column: {text_column}")
        logger.info(f"📊 Sample text lengths: {df[text_column].str.split().str.len().describe()}")
        
        # Text cleaning in parallel
        def clean_single_text(text):
            if pd.isna(text) or not isinstance(text, str):
                return None
            
            # Normalize text
            text = text.lower().strip()
            text = re.sub(r'\s+', ' ', text)  # Collapse whitespace
            
            # Remove control characters
            text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
            
            # Mask PII
            for pii_type, pattern in self.pii_patterns.items():
                text = re.sub(pattern, f'[REDACTED_{pii_type.upper()}]', text)
            
            # Length check
            word_count = len(text.split())
            if word_count < self.quality_thresholds['min_text_length']:
                return None
            if word_count > self.quality_thresholds['max_text_length']:
                text = ' '.join(text.split()[:self.quality_thresholds['max_text_length']])
            
            return text
        
        # Clean text in parallel
        with ThreadPoolExecutor(max_workers=self.n_cores) as executor:
            cleaned_texts = list(executor.map(clean_single_text, df[text_column]))
        
        df['cleaned_text'] = cleaned_texts
        df = df.dropna(subset=['cleaned_text'])
        
        logger.info(f"✅ Text cleaning complete. {len(df)} samples remaining")
        return df

    def remove_text_duplicates_optimized(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicates using optimized algorithms"""
        logger.info("🔄 Removing text duplicates...")
        
        if df.empty:
            return df
        
        # Create hash for exact duplicates
        df['text_hash'] = df['cleaned_text'].apply(lambda x: hashlib.sha256(x.encode()).hexdigest())
        
        # Remove exact duplicates
        df = df.drop_duplicates(subset=['text_hash'])
        logger.info(f"📊 After exact deduplication: {len(df)} samples")
        
        # Near-duplicate detection using TF-IDF (sampled for large datasets)
        if len(df) > 10000:
            # Sample for efficiency
            sample_size = min(10000, len(df))
            sample_df = df.sample(n=sample_size, random_state=42)
            
            # TF-IDF vectorization
            vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(sample_df['cleaned_text'])
            
            # Find similar documents
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Remove near-duplicates (similarity > 0.9)
            to_remove = set()
            for i in range(len(similarity_matrix)):
                for j in range(i+1, len(similarity_matrix)):
                    if similarity_matrix[i][j] > 0.9:
                        to_remove.add(j)
            
            # Apply to full dataset
            df = df.drop(df.index[list(to_remove)])
            logger.info(f"📊 After near-duplicate removal: {len(df)} samples")
        
        return df.drop(['text_hash'], axis=1)

    def clean_image_data_parallel(self, df: pd.DataFrame, label_map: Dict) -> pd.DataFrame:
        """Clean image data using parallel processing"""
        logger.info("🖼️  Cleaning image data...")
        
        if df.empty:
            return df
        
        # Apply label mapping
        def apply_labels(row):
            source_dataset = row.get('source_dataset', '')
            if source_dataset in label_map:
                mapping = label_map[source_dataset]
                return pd.Series({
                    'category': mapping['category'],
                    'subcategory': mapping['subcategory'],
                    'document_type': mapping['document_type']
                })
            else:
                return pd.Series({
                    'category': 'Other',
                    'subcategory': 'general',
                    'document_type': 'image'
                })
        
        label_results = df.apply(apply_labels, axis=1)
        df = pd.concat([df, label_results], axis=1)
        
        # Image validation in parallel
        def validate_image(row):
            try:
                image_path = row.get('image_path', row.get('file_path', ''))
                if not image_path or not os.path.exists(image_path):
                    return False
                
                # Basic image validation
                with Image.open(image_path) as img:
                    width, height = img.size
                    if min(width, height) < self.quality_thresholds['min_image_size']:
                        return False
                
                return True
            except:
                return False
        
        # Validate images in parallel
        with ThreadPoolExecutor(max_workers=self.n_cores) as executor:
            valid_images = list(executor.map(validate_image, [row for _, row in df.iterrows()]))
        
        df['is_valid'] = valid_images
        df = df[df['is_valid'] == True]
        df = df.drop(['is_valid'], axis=1)
        
        logger.info(f"✅ Image cleaning complete. {len(df)} samples remaining")
        return df

    def remove_image_duplicates_optimized(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove image duplicates using optimized algorithms"""
        logger.info("🔄 Removing image duplicates...")
        
        if df.empty:
            return df
        
        # Create file hash for exact duplicates
        def get_file_hash(image_path):
            try:
                with open(image_path, 'rb') as f:
                    return hashlib.sha256(f.read()).hexdigest()
            except:
                return None
        
        # Get file hashes in parallel
        with ThreadPoolExecutor(max_workers=self.n_cores) as executor:
            file_hashes = list(executor.map(
                get_file_hash, 
                df['image_path'] if 'image_path' in df.columns else df['file_path']
            ))
        
        df['file_hash'] = file_hashes
        df = df.dropna(subset=['file_hash'])
        
        # Remove exact duplicates
        df = df.drop_duplicates(subset=['file_hash'])
        logger.info(f"📊 After exact deduplication: {len(df)} samples")
        
        # Near-duplicate detection using perceptual hashing (sampled for large datasets)
        if len(df) > 5000:
            sample_size = min(5000, len(df))
            sample_df = df.sample(n=sample_size, random_state=42)
            
            def get_perceptual_hash(image_path):
                try:
                    with Image.open(image_path) as img:
                        return str(imagehash.average_hash(img))
                except:
                    return None
            
            # Get perceptual hashes in parallel
            with ThreadPoolExecutor(max_workers=self.n_cores) as executor:
                perceptual_hashes = list(executor.map(
                    get_perceptual_hash,
                    sample_df['image_path'] if 'image_path' in sample_df.columns else sample_df['file_path']
                ))
            
            sample_df['perceptual_hash'] = perceptual_hashes
            
            # Remove near-duplicates (Hamming distance <= 5)
            to_remove = set()
            for i in range(len(sample_df)):
                for j in range(i+1, len(sample_df)):
                    if (sample_df.iloc[i]['perceptual_hash'] and 
                        sample_df.iloc[j]['perceptual_hash']):
                        hamming_dist = sum(c1 != c2 for c1, c2 in zip(
                            sample_df.iloc[i]['perceptual_hash'], 
                            sample_df.iloc[j]['perceptual_hash']
                        ))
                        if hamming_dist <= 5:
                            to_remove.add(j)
            
            # Apply to full dataset
            df = df.drop(df.index[list(to_remove)])
            logger.info(f"📊 After near-duplicate removal: {len(df)} samples")
        
        return df.drop(['file_hash'], axis=1)

    def create_leakage_proof_splits(self, text_df: pd.DataFrame, image_df: pd.DataFrame) -> Dict:
        """Create train/val/test splits with leakage prevention"""
        logger.info("✂️  Creating leakage-proof splits...")
        
        splits = {}
        
        # Text data splits
        if not text_df.empty:
            # Ensure category column is string type and clean
            text_df['category'] = text_df['category'].astype(str)
            
            # Remove any duplicate category columns that might exist
            category_cols = [col for col in text_df.columns if 'category' in col.lower()]
            if len(category_cols) > 1:
                # Keep only the main category column
                for col in category_cols[1:]:
                    text_df = text_df.drop(columns=[col])
            
            # Ensure we have exactly one category column
            if 'category' not in text_df.columns:
                text_df['category'] = 'Other'
            
            logger.info(f"📊 Text categories: {text_df['category'].value_counts().to_dict()}")
            logger.info(f"📊 Source types: {text_df['source_type'].value_counts().to_dict()}")
            
            # Create group IDs for leakage prevention
            text_df['group_id'] = text_df.apply(
                lambda x: f"{x.get('source_dataset', 'unknown')}_{x.get('category', 'other')}_{hash(x.get('cleaned_text', '')) % 1000}", 
                axis=1
            )
            
            # Stratified split by category
            splitter = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=42)
            
            # Get split indices
            for fold, (train_idx, test_idx) in enumerate(splitter.split(
                text_df, text_df['category'], groups=text_df['group_id']
            )):
                if fold == 0:  # Use first fold
                    # Further split test into val and test
                    val_size = len(test_idx) // 2
                    val_idx = test_idx[:val_size]
                    test_idx = test_idx[val_size:]
                    
                    splits['text'] = {
                        'train': text_df.iloc[train_idx],
                        'val': text_df.iloc[val_idx],
                        'test': text_df.iloc[test_idx]
                    }
                    break
        
        # Image data splits
        if not image_df.empty:
            # Ensure category column is string type and clean
            image_df['category'] = image_df['category'].astype(str)
            
            # Remove any duplicate category columns that might exist
            category_cols = [col for col in image_df.columns if 'category' in col.lower()]
            if len(category_cols) > 1:
                # Keep only the main category column
                for col in category_cols[1:]:
                    image_df = image_df.drop(columns=[col])
            
            # Ensure we have exactly one category column
            if 'category' not in image_df.columns:
                image_df['category'] = 'Other'
            
            logger.info(f"📊 Image categories: {image_df['category'].value_counts().to_dict()}")
            logger.info(f"📊 Source types: {image_df['source_type'].value_counts().to_dict()}")
            
            # Create group IDs for leakage prevention
            image_df['group_id'] = image_df.apply(
                lambda x: f"{x.get('source_dataset', 'unknown')}_{x.get('category', 'other')}_{hash(str(x.get('image_path', ''))) % 1000}", 
                axis=1
            )
            
            # Stratified split by category
            splitter = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=42)
            
            # Get split indices
            for fold, (train_idx, test_idx) in enumerate(splitter.split(
                image_df, image_df['category'], groups=image_df['group_id']
            )):
                if fold == 0:  # Use first fold
                    # Further split test into val and test
                    val_size = len(test_idx) // 2
                    val_idx = test_idx[:val_size]
                    test_idx = test_idx[val_size:]
                    
                    splits['image'] = {
                        'train': image_df.iloc[train_idx],
                        'val': image_df.iloc[val_idx],
                        'test': image_df.iloc[test_idx]
                    }
                    break
        
        logger.info("✅ Splits created successfully")
        return splits

    def clean_duplicate_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate columns that might have been created during processing"""
        logger.info("🧹 Cleaning duplicate columns...")
        
        # Get duplicate column names
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicate_cols:
            logger.info(f"🔍 Found duplicate columns: {duplicate_cols}")
            
            # Keep only the first occurrence of each column
            df = df.loc[:, ~df.columns.duplicated()]
            logger.info(f"✅ Removed {len(duplicate_cols)} duplicate columns")
        
        return df

    def save_splits(self, splits: Dict):
        """Save processed splits to output directory"""
        logger.info("💾 Saving processed splits...")
        
        for data_type, data_splits in splits.items():
            for split_name, split_data in data_splits.items():
                if not split_data.empty:
                    # Clean duplicate columns before saving
                    split_data = self.clean_duplicate_columns(split_data)
                    
                    # Save as parquet
                    output_file = self.output_dir / f"{data_type}_{split_name}.parquet"
                    split_data.to_parquet(output_file, index=False)
                    
                    # Save as CSV for compatibility
                    csv_file = self.output_dir / f"{data_type}_{split_name}.csv"
                    split_data.to_csv(csv_file, index=False)
                    
                    logger.info(f"💾 Saved {data_type}_{split_name}: {len(split_data)} samples")

    def create_manifest(self, splits: Dict):
        """Create manifest file with dataset statistics"""
        logger.info("📋 Creating manifest...")
        
        manifest_data = []
        
        for data_type, data_splits in splits.items():
            for split_name, split_data in data_splits.items():
                if not split_data.empty:
                    # Category distribution
                    category_counts = split_data['category'].value_counts().to_dict()
                    source_type_counts = split_data['source_type'].value_counts().to_dict()
                    
                    for category, count in category_counts.items():
                        manifest_data.append({
                            'data_type': data_type,
                            'split': split_name,
                            'category': category,
                            'count': count,
                            'total_samples': len(split_data),
                            'synthetic_count': source_type_counts.get('synthetic', 0),
                            'real_count': source_type_counts.get('real', 0)
                        })
        
        manifest_df = pd.DataFrame(manifest_data)
        manifest_file = self.output_dir / 'manifest.csv'
        manifest_df.to_csv(manifest_file, index=False)
        
        logger.info(f"📋 Manifest created: {manifest_file}")

    def run_full_pipeline(self):
        """Run the complete optimized cleaning pipeline"""
        start_time = pd.Timestamp.now()
        logger.info("🚀 Starting Optimized Classification Data Cleaning Pipeline")
        
        try:
            # Step 1: Create label mapping
            label_map = self.create_label_mapping()
            
            # Step 2: Collect data in parallel
            text_df, image_df = self.collect_data_parallel()
            
            # Step 3: Clean text data in parallel
            if not text_df.empty:
                text_df = self.clean_text_parallel(text_df, label_map)
                text_df = self.remove_text_duplicates_optimized(text_df)
            
            # Step 4: Clean image data in parallel
            if not image_df.empty:
                image_df = self.clean_image_data_parallel(image_df, label_map)
                image_df = self.remove_image_duplicates_optimized(image_df)
            
            # Step 5: Create leakage-proof splits
            splits = self.create_leakage_proof_splits(text_df, image_df)
            
            # Step 6: Save splits
            self.save_splits(splits)
            
            # Step 7: Create manifest
            self.create_manifest(splits)
            
            # Final summary
            end_time = pd.Timestamp.now()
            duration = end_time - start_time
            
            logger.info("🎉 Pipeline completed successfully!")
            logger.info(f"⏱️  Total time: {duration}")
            
            # Print summary
            for data_type, data_splits in splits.items():
                logger.info(f"\n📊 {data_type.upper()} DATA SUMMARY:")
                for split_name, split_data in data_splits.items():
                    if not split_data.empty:
                        logger.info(f"  {split_name}: {len(split_data)} samples")
                        category_dist = split_data['category'].value_counts()
                        source_type_dist = split_data['source_type'].value_counts()
                        for category, count in category_dist.items():
                            logger.info(f"    {category}: {count}")
                        logger.info(f"    Source types: {source_type_dist.to_dict()}")
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            raise

if __name__ == "__main__":
    cleaner = OptimizedDataCleaner()
    cleaner.run_full_pipeline()
