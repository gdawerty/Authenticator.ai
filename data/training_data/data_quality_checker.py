#!/usr/bin/env python3
"""
Data Quality Checker for Authentia.ai
Handles data cleaning, PII detection, deduplication, and quality validation
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
import hashlib
from PIL import Image
import imagehash
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataQualityChecker:
    def __init__(self, base_dir: str = "/Users/prathamsaurabh/Authenticator.ai/data/training_data"):
        self.base_dir = Path(base_dir)
        self.processed_dir = self.base_dir / "processed_datasets"
        self.cleaned_dir = self.base_dir / "cleaned_datasets"
        
        # Create directories
        self.cleaned_dir.mkdir(exist_ok=True)
        
        # Download NLTK data if not available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        # PII patterns
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            'address': r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way|Place|Pl)\b',
            'zip_code': r'\b\d{5}(?:-\d{4})?\b',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'name': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        }
        
        # Data quality thresholds
        self.min_text_length = 50
        self.max_text_length = 10000
        self.min_image_size = (100, 100)
        self.max_image_size = (2048, 2048)
        self.max_duplicate_threshold = 0.95  # Similarity threshold for duplicates
        
    def clean_text_data(self, input_file: str, output_file: str = None) -> pd.DataFrame:
        """Clean and prepare text data for training"""
        logger.info(f"Cleaning text data from {input_file}")
        
        # Read input file
        if input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
        elif input_file.endswith('.json'):
            df = pd.read_json(input_file)
        else:
            raise ValueError(f"Unsupported file format: {input_file}")
        
        initial_count = len(df)
        logger.info(f"Initial text samples: {initial_count}")
        
        # Step 1: Remove duplicates
        df = self._remove_text_duplicates(df)
        
        # Step 2: Clean text content
        df = self._clean_text_content(df)
        
        # Step 3: Handle PII
        df = self._handle_pii(df)
        
        # Step 4: Filter by quality
        df = self._filter_text_quality(df)
        
        # Step 5: Validate categories
        df = self._validate_categories(df)
        
        final_count = len(df)
        logger.info(f"Final text samples: {final_count} (removed {initial_count - final_count})")
        
        # Save cleaned data
        if output_file is None:
            output_file = str(self.cleaned_dir / f"cleaned_{Path(input_file).name}")
        
        df.to_csv(output_file, index=False)
        logger.info(f"Cleaned text data saved to {output_file}")
        
        return df
    
    def clean_image_data(self, input_file: str, output_file: str = None) -> pd.DataFrame:
        """Clean and prepare image data for training"""
        logger.info(f"Cleaning image data from {input_file}")
        
        # Read input file
        if input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
        elif input_file.endswith('.json'):
            df = pd.read_json(input_file)
        else:
            raise ValueError(f"Unsupported file format: {input_file}")
        
        initial_count = len(df)
        logger.info(f"Initial image samples: {initial_count}")
        
        # Step 1: Remove duplicates
        df = self._remove_image_duplicates(df)
        
        # Step 2: Validate image files
        df = self._validate_image_files(df)
        
        # Step 3: Filter by quality
        df = self._filter_image_quality(df)
        
        # Step 4: Validate categories
        df = self._validate_categories(df)
        
        final_count = len(df)
        logger.info(f"Final image samples: {final_count} (removed {initial_count - final_count})")
        
        # Save cleaned data
        if output_file is None:
            output_file = str(self.cleaned_dir / f"cleaned_{Path(input_file).name}")
        
        df.to_csv(output_file, index=False)
        logger.info(f"Cleaned image data saved to {output_file}")
        
        return df
    
    def _remove_text_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate text entries"""
        logger.info("Removing text duplicates...")
        
        initial_count = len(df)
        
        # Create text hash for deduplication
        df['text_hash'] = df['text'].apply(lambda x: hashlib.md5(str(x).encode()).hexdigest())
        
        # Remove exact duplicates
        df = df.drop_duplicates(subset=['text_hash'])
        
        # Remove near-duplicates using similarity
        df = self._remove_near_duplicates(df)
        
        # Remove hash column
        df = df.drop(columns=['text_hash'])
        
        final_count = len(df)
        logger.info(f"Removed {initial_count - final_count} text duplicates")
        
        return df
    
    def _remove_image_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate image entries"""
        logger.info("Removing image duplicates...")
        
        initial_count = len(df)
        
        # Calculate perceptual hashes for images
        df['image_hash'] = df['image_path'].apply(self._calculate_image_hash)
        
        # Remove exact duplicates
        df = df.drop_duplicates(subset=['image_hash'])
        
        # Remove near-duplicates using similarity
        df = self._remove_near_duplicates(df, column='image_hash')
        
        # Remove hash column
        df = df.drop(columns=['image_hash'])
        
        final_count = len(df)
        logger.info(f"Removed {initial_count - final_count} image duplicates")
        
        return df
    
    def _calculate_image_hash(self, image_path: str) -> str:
        """Calculate perceptual hash for an image"""
        try:
            img = Image.open(image_path)
            # Resize to consistent size for hash calculation
            img = img.resize((8, 8), Image.Resampling.LANCZOS)
            # Convert to grayscale
            img = img.convert('L')
            # Calculate hash
            hash_value = imagehash.average_hash(img)
            return str(hash_value)
        except Exception as e:
            logger.warning(f"Error calculating hash for {image_path}: {e}")
            return hashlib.md5(image_path.encode()).hexdigest()
    
    def _remove_near_duplicates(self, df: pd.DataFrame, column: str = 'text_hash') -> pd.DataFrame:
        """Remove near-duplicate entries based on similarity"""
        logger.info("Removing near-duplicates...")
        
        # Group by category to avoid cross-category deduplication
        df_clean = []
        
        for category in df['category'].unique():
            category_df = df[df['category'] == category].copy()
            
            if len(category_df) <= 1:
                df_clean.append(category_df)
                continue
            
            # Calculate similarity matrix (simplified approach)
            to_remove = set()
            
            for i in range(len(category_df)):
                if i in to_remove:
                    continue
                
                for j in range(i + 1, len(category_df)):
                    if j in to_remove:
                        continue
                    
                    # Calculate similarity (this is a simplified approach)
                    similarity = self._calculate_similarity(
                        category_df.iloc[i][column],
                        category_df.iloc[j][column]
                    )
                    
                    if similarity > self.max_duplicate_threshold:
                        to_remove.add(j)
            
            # Remove duplicates
            category_df = category_df.drop(category_df.index[list(to_remove)])
            df_clean.append(category_df)
        
        return pd.concat(df_clean, ignore_index=True)
    
    def _calculate_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between two hashes"""
        if len(hash1) != len(hash2):
            return 0.0
        
        # For perceptual hashes, calculate Hamming distance
        if len(hash1) == 64:  # 64-bit hash
            distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
            return 1.0 - (distance / 64.0)
        
        # For MD5 hashes, exact match
        return 1.0 if hash1 == hash2 else 0.0
    
    def _clean_text_content(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize text content"""
        logger.info("Cleaning text content...")
        
        # Clean text column
        df['text'] = df['text'].astype(str).apply(self._clean_single_text)
        
        # Remove empty or very short texts
        df = df[df['text'].str.len() >= self.min_text_length]
        
        # Truncate very long texts
        df['text'] = df['text'].apply(lambda x: x[:self.max_text_length] if len(x) > self.max_text_length else x)
        
        return df
    
    def _clean_single_text(self, text: str) -> str:
        """Clean a single text entry"""
        if pd.isna(text):
            return ""
        
        # Convert to string
        text = str(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Normalize whitespace
        text = text.strip()
        
        return text
    
    def _handle_pii(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect and handle PII in text data"""
        logger.info("Handling PII...")
        
        # Create PII detection columns
        pii_columns = {}
        for pii_type, pattern in self.pii_patterns.items():
            pii_columns[f'has_{pii_type}'] = df['text'].str.contains(pattern, regex=True, case=False)
        
        # Add PII detection to dataframe
        for col_name, col_data in pii_columns.items():
            df[col_name] = col_data
        
        # Mask PII in text
        df['text'] = df['text'].apply(self._mask_pii)
        
        # Log PII statistics
        pii_stats = {col: df[col].sum() for col in pii_columns.keys()}
        logger.info(f"PII detected: {pii_stats}")
        
        return df
    
    def _mask_pii(self, text: str) -> str:
        """Mask PII in text"""
        # Mask email addresses
        text = re.sub(self.pii_patterns['email'], '[EMAIL]', text)
        
        # Mask phone numbers
        text = re.sub(self.pii_patterns['phone'], '[PHONE]', text)
        
        # Mask SSNs
        text = re.sub(self.pii_patterns['ssn'], '[SSN]', text)
        
        # Mask credit card numbers
        text = re.sub(self.pii_patterns['credit_card'], '[CREDIT_CARD]', text)
        
        # Mask addresses
        text = re.sub(self.pii_patterns['address'], '[ADDRESS]', text)
        
        # Mask zip codes
        text = re.sub(self.pii_patterns['zip_code'], '[ZIP_CODE]', text)
        
        # Mask dates (keep format but mask specific dates)
        text = re.sub(self.pii_patterns['date'], '[DATE]', text)
        
        # Mask names (keep first letter, mask rest)
        text = re.sub(self.pii_patterns['name'], lambda m: m.group()[0] + '*' * (len(m.group()) - 1), text)
        
        return text
    
    def _validate_image_files(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate that image files exist and are accessible"""
        logger.info("Validating image files...")
        
        valid_images = []
        
        for _, row in df.iterrows():
            image_path = row['image_path']
            
            try:
                # Check if file exists
                if not os.path.exists(image_path):
                    logger.warning(f"Image file not found: {image_path}")
                    continue
                
                # Try to open image
                with Image.open(image_path) as img:
                    # Check image size
                    if img.size[0] < self.min_image_size[0] or img.size[1] < self.min_image_size[1]:
                        logger.warning(f"Image too small: {image_path} ({img.size})")
                        continue
                    
                    if img.size[0] > self.max_image_size[0] or img.size[1] > self.max_image_size[1]:
                        logger.warning(f"Image too large: {image_path} ({img.size})")
                        continue
                    
                    # Check if image is corrupted
                    img.verify()
                    
                    valid_images.append(row)
                    
            except Exception as e:
                logger.warning(f"Error validating image {image_path}: {e}")
                continue
        
        return pd.DataFrame(valid_images)
    
    def _filter_text_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter text data by quality metrics"""
        logger.info("Filtering text by quality...")
        
        initial_count = len(df)
        
        # Remove texts with too many special characters
        special_char_ratio = df['text'].apply(lambda x: len(re.findall(r'[^\w\s]', x)) / len(x) if len(x) > 0 else 0)
        df = df[special_char_ratio < 0.3]  # Less than 30% special characters
        
        # Remove texts with too many numbers (likely not natural text)
        number_ratio = df['text'].apply(lambda x: len(re.findall(r'\d', x)) / len(x) if len(x) > 0 else 0)
        df = df[number_ratio < 0.4]  # Less than 40% numbers
        
        # Remove texts that are mostly whitespace
        whitespace_ratio = df['text'].apply(lambda x: len(re.findall(r'\s', x)) / len(x) if len(x) > 0 else 0)
        df = df[whitespace_ratio < 0.5]  # Less than 50% whitespace
        
        final_count = len(df)
        logger.info(f"Quality filtering removed {initial_count - final_count} samples")
        
        return df
    
    def _filter_image_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter image data by quality metrics"""
        logger.info("Filtering images by quality...")
        
        initial_count = len(df)
        
        # This would include more sophisticated image quality checks
        # For now, we'll just ensure the images are valid
        
        final_count = len(df)
        logger.info(f"Quality filtering removed {initial_count - final_count} samples")
        
        return df
    
    def _validate_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and standardize category labels"""
        logger.info("Validating categories...")
        
        # Define valid categories
        valid_categories = ['education', 'insurance', 'legal', 'resume_employment', 'other']
        
        # Clean category names
        df['category'] = df['category'].str.lower().str.strip()
        
        # Map similar categories
        category_mapping = {
            'k12_education': 'education',
            'k12_administrative': 'education',
            'general_document_classification': 'other',
            'vision_datasets': 'other',
            'forgery_vlm': 'other'
        }
        
        df['category'] = df['category'].map(lambda x: category_mapping.get(x, x))
        
        # Filter out invalid categories
        df = df[df['category'].isin(valid_categories)]
        
        # Log category distribution
        category_counts = df['category'].value_counts()
        logger.info(f"Category distribution: {category_counts.to_dict()}")
        
        return df
    
    def generate_quality_report(self, df: pd.DataFrame, data_type: str) -> Dict:
        """Generate a comprehensive quality report for the dataset"""
        logger.info(f"Generating quality report for {data_type} data")
        
        report = {
            "data_type": data_type,
            "generated_at": datetime.now().isoformat(),
            "total_samples": len(df),
            "category_distribution": df['category'].value_counts().to_dict(),
            "quality_metrics": {}
        }
        
        if data_type == "text":
            # Text-specific metrics
            text_lengths = df['text'].str.len()
            report["quality_metrics"] = {
                "avg_text_length": float(text_lengths.mean()) if not pd.isna(text_lengths.mean()) else 0.0,
                "min_text_length": int(text_lengths.min()) if not pd.isna(text_lengths.min()) else 0,
                "max_text_length": int(text_lengths.max()) if not pd.isna(text_lengths.max()) else 0,
                "text_length_std": float(text_lengths.std()) if not pd.isna(text_lengths.std()) else 0.0
            }
            
            # PII detection summary
            pii_columns = [col for col in df.columns if col.startswith('has_')]
            if pii_columns:
                pii_summary = {}
                for col in pii_columns:
                    pii_summary[col] = int(df[col].sum())  # Convert numpy int64 to Python int
                report["pii_detection"] = pii_summary
        
        elif data_type == "image":
            # Image-specific metrics
            report["quality_metrics"] = {
                "image_count": len(df),
                "unique_sources": df['source'].nunique() if 'source' in df.columns else 0
            }
        
        # Save report
        report_file = self.cleaned_dir / f"quality_report_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Quality report saved to {report_file}")
        return report
    
    def run_full_cleaning_pipeline(self, text_files: List[str] = None, image_files: List[str] = None):
        """Run the complete data cleaning pipeline"""
        logger.info("🧹 Starting Data Quality Cleaning Pipeline")
        
        cleaned_data = {}
        
        # Clean text data
        if text_files:
            for text_file in text_files:
                logger.info(f"Cleaning text file: {text_file}")
                cleaned_df = self.clean_text_data(text_file)
                cleaned_data[f"text_{Path(text_file).stem}"] = cleaned_df
                
                # Generate quality report
                self.generate_quality_report(cleaned_df, "text")
        
        # Clean image data
        if image_files:
            for image_file in image_files:
                logger.info(f"Cleaning image file: {image_file}")
                cleaned_df = self.clean_image_data(image_file)
                cleaned_data[f"image_{Path(image_file).stem}"] = cleaned_df
                
                # Generate quality report
                self.generate_quality_report(cleaned_df, "image")
        
        # Generate overall summary
        summary = {
            "pipeline_completed_at": datetime.now().isoformat(),
            "files_processed": len(cleaned_data),
            "cleaned_datasets": list(cleaned_data.keys())
        }
        
        summary_file = self.cleaned_dir / "cleaning_pipeline_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("🎉 Data Quality Cleaning Pipeline completed!")
        logger.info(f"Summary saved to {summary_file}")
        
        return cleaned_data

if __name__ == "__main__":
    # Example usage
    checker = DataQualityChecker()
    
    # Find files to clean
    processed_dir = Path("/Users/prathamsaurabh/Authenticator.ai/data/training_data/processed_datasets")
    
    text_files = list(processed_dir.rglob("*_synthetic.csv"))
    image_files = list(processed_dir.rglob("*_metadata.csv"))
    
    # Run cleaning pipeline
    cleaned_data = checker.run_full_cleaning_pipeline(
        text_files=[str(f) for f in text_files],
        image_files=[str(f) for f in image_files]
    )
