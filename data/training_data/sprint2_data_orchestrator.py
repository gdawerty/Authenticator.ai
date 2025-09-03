#!/usr/bin/env python3
"""
Sprint 2 Data Orchestrator for Authentia.ai
Handles data cleaning, synthetic generation, and train/val/test splits
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import shutil
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
import hashlib
from PIL import Image, ImageDraw, ImageFont
import random
import string

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Sprint2DataOrchestrator:
    def __init__(self, base_dir: str = "/Users/prathamsaurabh/Authenticator.ai/data/training_data"):
        self.base_dir = Path(base_dir)
        self.raw_datasets_dir = self.base_dir / "raw_datasets"
        self.processed_dir = self.base_dir / "processed_datasets"
        self.splits_dir = self.base_dir / "model_splits"
        
        # Create directories
        self.processed_dir.mkdir(exist_ok=True)
        self.splits_dir.mkdir(exist_ok=True)
        
        # Sprint 2 Categories and Subtypes
        self.categories = {
            "education": {
                "subtypes": ["transcript", "report_card", "attendance_log", "immunization_form"],
                "priority": "high"
            },
            "insurance": {
                "subtypes": ["accident_claim", "policy_form", "invoice", "medical_record"],
                "priority": "high"
            },
            "legal": {
                "subtypes": ["nda", "contract", "lease", "service_agreement"],
                "priority": "medium"
            },
            "resume_employment": {
                "subtypes": ["resume", "cover_letter", "reference_letter", "certification"],
                "priority": "medium"
            },
            "other": {
                "subtypes": ["general_document", "form", "letter"],
                "priority": "low"
            }
        }
        
        # Data quality thresholds
        self.min_text_length = 50
        self.min_image_size = (100, 100)
        self.max_image_size = (2048, 2048)
        
    def get_dataset_status(self) -> Dict:
        """Get current status of all datasets"""
        status = {
            "total_datasets": 0,
            "ready_datasets": 0,
            "failed_datasets": 0,
            "categories_covered": set(),
            "estimated_samples": 0
        }
        
        for category_dir in self.raw_datasets_dir.iterdir():
            if category_dir.is_dir():
                for dataset_dir in category_dir.iterdir():
                    if dataset_dir.is_dir():
                        status["total_datasets"] += 1
                        
                        # Check if dataset has data
                        if self._has_valid_data(dataset_dir):
                            status["ready_datasets"] += 1
                            status["categories_covered"].add(category_dir.name)
                            status["estimated_samples"] += self._count_samples(dataset_dir)
                        else:
                            status["failed_datasets"] += 1
        
        status["categories_covered"] = list(status["categories_covered"])
        return status
    
    def _has_valid_data(self, dataset_dir: Path) -> bool:
        """Check if dataset directory has valid data"""
        # Look for common data files
        data_files = list(dataset_dir.rglob("*.json")) + list(dataset_dir.rglob("*.csv")) + \
                    list(dataset_dir.rglob("*.arrow")) + list(dataset_dir.rglob("*.parquet"))
        
        # Look for image files
        image_files = list(dataset_dir.rglob("*.jpg")) + list(dataset_dir.rglob("*.png")) + \
                     list(dataset_dir.rglob("*.jpeg"))
        
        return len(data_files) > 0 or len(image_files) > 0
    
    def _count_samples(self, dataset_dir: Path) -> int:
        """Estimate number of samples in dataset"""
        # This is a rough estimate - actual implementation would be more sophisticated
        data_files = list(dataset_dir.rglob("*.json")) + list(dataset_dir.rglob("*.csv"))
        image_files = list(dataset_dir.rglob("*.jpg")) + list(dataset_dir.rglob("*.png"))
        
        return len(data_files) + len(image_files)
    
    def generate_synthetic_data(self, target_samples_per_category: int = 1000) -> Dict:
        """Generate synthetic data to fill gaps"""
        logger.info(f"Generating synthetic data for {target_samples_per_category} samples per category")
        
        synthetic_data = {
            "text": {},
            "image": {}
        }
        
        for category, config in self.categories.items():
            if config["priority"] in ["high", "medium"]:
                logger.info(f"Generating synthetic data for {category}")
                
                # Generate text data
                synthetic_data["text"][category] = self._generate_synthetic_text(
                    category, config["subtypes"], target_samples_per_category // 2
                )
                
                # Generate image data
                synthetic_data["image"][category] = self._generate_synthetic_images(
                    category, config["subtypes"], target_samples_per_category // 2
                )
        
        # Save synthetic data
        self._save_synthetic_data(synthetic_data)
        return synthetic_data
    
    def _generate_synthetic_text(self, category: str, subtypes: List[str], num_samples: int) -> List[Dict]:
        """Generate synthetic text data for a category"""
        samples = []
        
        for _ in range(num_samples):
            subtype = random.choice(subtypes)
            
            if category == "education":
                if subtype == "transcript":
                    text = self._generate_transcript_text()
                elif subtype == "report_card":
                    text = self._generate_report_card_text()
                else:
                    text = self._generate_generic_education_text(subtype)
            
            elif category == "insurance":
                if subtype == "accident_claim":
                    text = self._generate_accident_claim_text()
                else:
                    text = self._generate_generic_insurance_text(subtype)
            
            elif category == "legal":
                text = self._generate_legal_document_text(subtype)
            
            elif category == "resume_employment":
                text = self._generate_resume_text(subtype)
            
            else:
                text = self._generate_generic_text(subtype)
            
            samples.append({
                "text": text,
                "category": category,
                "subtype": subtype,
                "is_synthetic": True,
                "generated_at": datetime.now().isoformat()
            })
        
        return samples
    
    def _generate_synthetic_images(self, category: str, subtypes: List[str], num_samples: int) -> List[Dict]:
        """Generate synthetic image data for a category"""
        samples = []
        
        for _ in range(num_samples):
            subtype = random.choice(subtypes)
            
            # Create a simple synthetic image
            img_path = self._create_synthetic_image(category, subtype)
            
            samples.append({
                "image_path": str(img_path),
                "category": category,
                "subtype": subtype,
                "is_synthetic": True,
                "generated_at": datetime.now().isoformat()
            })
        
        return samples
    
    def _generate_transcript_text(self) -> str:
        """Generate synthetic transcript text"""
        courses = ["Mathematics", "English", "Science", "History", "Art", "Physical Education"]
        grades = ["A", "B", "C", "D", "F"]
        
        transcript = "STUDENT TRANSCRIPT\n"
        transcript += "Academic Year: 2023-2024\n\n"
        
        for course in random.sample(courses, random.randint(4, 6)):
            grade = random.choice(grades)
            credits = random.randint(1, 4)
            transcript += f"{course}: {grade} ({credits} credits)\n"
        
        transcript += f"\nGPA: {random.uniform(2.0, 4.0):.2f}"
        return transcript
    
    def _generate_report_card_text(self) -> str:
        """Generate synthetic report card text"""
        subjects = ["Math", "Reading", "Writing", "Science", "Social Studies"]
        performance_levels = ["Exceeds Expectations", "Meets Expectations", "Below Expectations"]
        
        report = "REPORT CARD\n"
        report += "Student: [Student Name]\n"
        report += "Grade: [Grade Level]\n\n"
        
        for subject in subjects:
            level = random.choice(performance_levels)
            report += f"{subject}: {level}\n"
        
        return report
    
    def _generate_accident_claim_text(self) -> str:
        """Generate synthetic accident claim text"""
        return f"""ACCIDENT CLAIM FORM
        
Claim Number: {random.randint(100000, 999999)}
Date of Accident: {datetime.now().strftime('%Y-%m-%d')}
        
Description: Vehicle was involved in a collision at the intersection of Main St and Oak Ave.
Damage Estimate: ${random.randint(1000, 15000)}
        
Witnesses: {random.randint(0, 2)} witnesses present
Police Report: Filed with local police department"""
    
    def _generate_legal_document_text(self, subtype: str) -> str:
        """Generate synthetic legal document text"""
        if subtype == "nda":
            return f"""NON-DISCLOSURE AGREEMENT
        
This Non-Disclosure Agreement (the "Agreement") is entered into on {datetime.now().strftime('%Y-%m-%d')}
between [Company Name] and [Employee Name].
        
1. CONFIDENTIAL INFORMATION
The Employee acknowledges that they may have access to confidential information.
        
2. NON-DISCLOSURE
The Employee agrees not to disclose any confidential information.
        
3. TERM
This Agreement shall remain in effect for {random.randint(1, 5)} years."""
        
        return f"Generic {subtype} document content..."
    
    def _generate_resume_text(self, subtype: str) -> str:
        """Generate synthetic resume text"""
        if subtype == "resume":
            return f"""PROFESSIONAL RESUME
        
[Full Name]
[Email] | [Phone] | [Location]
        
EXPERIENCE
Software Engineer - Tech Company (2020-Present)
- Developed web applications using React and Python
- Led team of {random.randint(2, 8)} developers
        
EDUCATION
Bachelor's in Computer Science - University Name (2020)
GPA: {random.uniform(3.0, 4.0):.1f}"""
        
        return f"Generic {subtype} content..."
    
    def _generate_generic_education_text(self, subtype: str) -> str:
        """Generate generic education text"""
        return f"Generic {subtype} document for educational purposes. This document contains standard educational content and formatting."
    
    def _generate_generic_insurance_text(self, subtype: str) -> str:
        """Generate generic insurance text"""
        return f"Generic {subtype} document for insurance purposes. This document contains standard insurance content and formatting."
    
    def _generate_generic_text(self, subtype: str) -> str:
        """Generate generic text"""
        return f"Generic {subtype} document. This document contains standard content and formatting for {subtype} purposes."
    
    def _create_synthetic_image(self, category: str, subtype: str) -> Path:
        """Create a simple synthetic image"""
        # Create output directory
        output_dir = self.processed_dir / "synthetic_images" / category / subtype
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a simple image with text
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add some text
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        text = f"{category.title()} - {subtype.replace('_', ' ').title()}"
        draw.text((50, 150), text, fill='black', font=font)
        
        # Save image
        filename = f"synthetic_{category}_{subtype}_{random.randint(1000, 9999)}.png"
        img_path = output_dir / filename
        img.save(img_path)
        
        return img_path
    
    def _save_synthetic_data(self, synthetic_data: Dict):
        """Save synthetic data to files"""
        # Save text data
        for category, samples in synthetic_data["text"].items():
            output_dir = self.processed_dir / "synthetic_text" / category
            output_dir.mkdir(parents=True, exist_ok=True)
            
            df = pd.DataFrame(samples)
            df.to_csv(output_dir / f"{category}_synthetic.csv", index=False)
        
        # Save image metadata
        for category, samples in synthetic_data["image"].items():
            output_dir = self.processed_dir / "synthetic_images" / category
            output_dir.mkdir(parents=True, exist_ok=True)
            
            df = pd.DataFrame(samples)
            df.to_csv(output_dir / f"{category}_synthetic_metadata.csv", index=False)
    
    def create_train_val_test_splits(self, test_size: float = 0.15, val_size: float = 0.15):
        """Create train/validation/test splits for all data"""
        logger.info("Creating train/validation/test splits...")
        
        # Collect all data
        all_text_data = self._collect_all_text_data()
        all_image_data = self._collect_all_image_data()
        
        # Create splits for text data
        text_splits = self._create_splits(all_text_data, test_size, val_size, "text")
        
        # Create splits for image data
        image_splits = self._create_splits(all_image_data, test_size, val_size, "image")
        
        # Save splits
        self._save_splits(text_splits, "text")
        self._save_splits(image_splits, "image")
        
        # Generate split summary
        self._generate_split_summary(text_splits, image_splits)
        
        return {"text": text_splits, "image": image_splits}
    
    def _collect_all_text_data(self) -> List[Dict]:
        """Collect all text data from various sources"""
        all_data = []
        
        # Collect from raw datasets
        for category_dir in self.raw_datasets_dir.iterdir():
            if category_dir.is_dir():
                for dataset_dir in category_dir.iterdir():
                    if dataset_dir.is_dir():
                        data = self._extract_text_from_dataset(dataset_dir, category_dir.name)
                        all_data.extend(data)
        
        # Collect synthetic data
        synthetic_text_dir = self.processed_dir / "synthetic_text"
        if synthetic_text_dir.exists():
            for category_dir in synthetic_text_dir.iterdir():
                if category_dir.is_dir():
                    for csv_file in category_dir.glob("*.csv"):
                        df = pd.read_csv(csv_file)
                        all_data.extend(df.to_dict('records'))
        
        return all_data
    
    def _collect_all_image_data(self) -> List[Dict]:
        """Collect all image data from various sources"""
        all_data = []
        
        # Collect from raw datasets
        for category_dir in self.raw_datasets_dir.iterdir():
            if category_dir.is_dir():
                for dataset_dir in category_dir.iterdir():
                    if dataset_dir.is_dir():
                        data = self._extract_images_from_dataset(dataset_dir, category_dir.name)
                        all_data.extend(data)
        
        # Collect synthetic data
        synthetic_image_dir = self.processed_dir / "synthetic_images"
        if synthetic_image_dir.exists():
            for category_dir in synthetic_image_dir.iterdir():
                if category_dir.is_dir():
                    for csv_file in category_dir.glob("*_metadata.csv"):
                        df = pd.read_csv(csv_file)
                        all_data.extend(df.to_dict('records'))
        
        return all_data
    
    def _extract_text_from_dataset(self, dataset_dir: Path, category: str) -> List[Dict]:
        """Extract text data from a dataset directory"""
        data = []
        
        # Look for common data files
        for json_file in dataset_dir.rglob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    content = json.load(f)
                    # This is a simplified extraction - actual implementation would be more sophisticated
                    if isinstance(content, dict):
                        text = str(content.get('text', content.get('content', str(content))))
                        if len(text) > self.min_text_length:
                            data.append({
                                "text": text,
                                "category": category,
                                "subtype": "general_document",
                                "source": str(dataset_dir),
                                "is_synthetic": False
                            })
            except Exception as e:
                logger.warning(f"Error reading {json_file}: {e}")
        
        return data
    
    def _extract_images_from_dataset(self, dataset_dir: Path, category: str) -> List[Dict]:
        """Extract image data from a dataset directory"""
        data = []
        
        # Look for image files
        for img_file in dataset_dir.rglob("*.jpg"):
            data.append({
                "image_path": str(img_file),
                "category": category,
                "subtype": "general_document",
                "source": str(dataset_dir),
                "is_synthetic": False
            })
        
        for img_file in dataset_dir.rglob("*.png"):
            data.append({
                "image_path": str(img_file),
                "category": category,
                "subtype": "general_document",
                "source": str(dataset_dir),
                "is_synthetic": False
            })
        
        return data
    
    def _create_splits(self, data: List[Dict], test_size: float, val_size: float, data_type: str) -> Dict:
        """Create train/validation/test splits"""
        if not data:
            logger.warning(f"No {data_type} data found")
            return {"train": [], "val": [], "test": []}
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data)
        
        # Stratify by category if possible
        try:
            # First split: train vs temp
            train_df, temp_df = train_test_split(
                df, test_size=test_size + val_size, 
                stratify=df['category'], random_state=42
            )
            
            # Second split: temp into val vs test
            val_size_adjusted = val_size / (test_size + val_size)
            val_df, test_df = train_test_split(
                temp_df, test_size=val_size_adjusted,
                stratify=temp_df['category'], random_state=42
            )
        except ValueError:
            # Fallback if stratification fails
            logger.warning(f"Stratification failed for {data_type}, using random split")
            train_df, temp_df = train_test_split(df, test_size=test_size + val_size, random_state=42)
            val_size_adjusted = val_size / (test_size + val_size)
            val_df, test_df = train_test_split(temp_df, test_size=val_size_adjusted, random_state=42)
        
        return {
            "train": train_df.to_dict('records'),
            "val": val_df.to_dict('records'),
            "test": test_df.to_dict('records')
        }
    
    def _save_splits(self, splits: Dict, data_type: str):
        """Save splits to files"""
        splits_dir = self.splits_dir / data_type
        splits_dir.mkdir(exist_ok=True)
        
        for split_name, data in splits.items():
            if data:
                df = pd.DataFrame(data)
                output_file = splits_dir / f"{split_name}.csv"
                df.to_csv(output_file, index=False)
                logger.info(f"Saved {split_name} split with {len(data)} samples to {output_file}")
    
    def _generate_split_summary(self, text_splits: Dict, image_splits: Dict):
        """Generate summary of all splits"""
        summary = {
            "generated_at": datetime.now().isoformat(),
            "text_data": {
                "train": len(text_splits["train"]),
                "val": len(text_splits["val"]),
                "test": len(text_splits["test"]),
                "total": len(text_splits["train"]) + len(text_splits["val"]) + len(text_splits["test"])
            },
            "image_data": {
                "train": len(image_splits["train"]),
                "val": len(image_splits["val"]),
                "test": len(image_splits["test"]),
                "total": len(image_splits["train"]) + len(image_splits["val"]) + len(image_splits["test"])
            }
        }
        
        # Save summary
        summary_file = self.splits_dir / "split_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Split summary saved to {summary_file}")
        return summary
    
    def run_full_pipeline(self):
        """Run the complete data processing pipeline"""
        logger.info("🚀 Starting Sprint 2 Data Processing Pipeline")
        
        # Step 1: Check current status
        status = self.get_dataset_status()
        logger.info(f"Current dataset status: {status}")
        
        # Step 2: Generate synthetic data
        logger.info("📊 Generating synthetic data...")
        synthetic_data = self.generate_synthetic_data(target_samples_per_category=1000)
        
        # Step 3: Create splits
        logger.info("✂️ Creating train/validation/test splits...")
        splits = self.create_train_val_test_splits()
        
        # Step 4: Generate final summary
        logger.info("📋 Generating final summary...")
        final_summary = {
            "pipeline_completed_at": datetime.now().isoformat(),
            "initial_status": status,
            "synthetic_data_generated": len(synthetic_data["text"]) + len(synthetic_data["image"]),
            "final_splits": {
                "text_total": splits["text"]["train"] + splits["text"]["val"] + splits["text"]["test"],
                "image_total": splits["image"]["train"] + splits["image"]["val"] + splits["image"]["test"]
            }
        }
        
        # Save final summary
        summary_file = self.base_dir / "pipeline_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(final_summary, f, indent=2)
        
        logger.info("🎉 Sprint 2 Data Processing Pipeline completed!")
        logger.info(f"Final summary saved to {summary_file}")
        
        return final_summary

if __name__ == "__main__":
    orchestrator = Sprint2DataOrchestrator()
    orchestrator.run_full_pipeline()

