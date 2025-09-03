#!/usr/bin/env python3
"""
Simple Dataset Downloader for Authentia.ai
Downloads working datasets from Hugging Face and other sources
"""

import os
import json
import requests
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleDatasetDownloader:
    def __init__(self, base_dir: str = "/Users/prathamsaurabh/Authenticator.ai/data/training_data"):
        self.base_dir = Path(base_dir)
        self.raw_datasets_dir = self.base_dir / "raw_datasets"
        
        # Working datasets that we know exist and work
        self.working_datasets = {
            "general_document_classification": {
                "ag_news": {
                    "source": "huggingface",
                    "hf_name": "ag_news",
                    "description": "News classification dataset",
                    "expected_samples": 120000
                },
                "imdb": {
                    "source": "huggingface", 
                    "hf_name": "imdb",
                    "description": "Movie review sentiment classification",
                    "expected_samples": 50000
                },
                "yelp_polarity": {
                    "source": "huggingface",
                    "hf_name": "yelp_polarity", 
                    "description": "Yelp review sentiment classification",
                    "expected_samples": 560000
                }
            },
            "k12_education": {
                "ai2_arc": {
                    "source": "huggingface",
                    "hf_name": "ai2_arc",
                    "config": "ARC-Challenge",
                    "description": "Science questions for K-12",
                    "expected_samples": 2590
                },
                "race": {
                    "source": "huggingface",
                    "hf_name": "race",
                    "config": "all",
                    "description": "Reading comprehension for K-12",
                    "expected_samples": 87000
                },
                "gsm8k": {
                    "source": "huggingface",
                    "hf_name": "gsm8k",
                    "config": "main",
                    "description": "Grade school math problems",
                    "expected_samples": 8300
                }
            },
            "resume_employment": {
                "fake_job_postings": {
                    "source": "manual",
                    "url": "https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction",
                    "description": "Real vs fake job postings",
                    "expected_samples": 17880
                }
            },
            "vision_datasets": {
                "mnist": {
                    "source": "huggingface",
                    "hf_name": "mnist",
                    "description": "Handwritten digits for OCR",
                    "expected_samples": 70000
                },
                "fashion_mnist": {
                    "source": "huggingface",
                    "hf_name": "fashion_mnist",
                    "description": "Fashion item classification",
                    "expected_samples": 70000
                }
            }
        }
    
    def download_huggingface_dataset(self, dataset_name: str, target_dir: Path, config: str = None) -> bool:
        """Download dataset from Hugging Face using datasets library"""
        try:
            logger.info(f"Downloading {dataset_name} from Hugging Face...")
            
            # Import here to avoid issues
            from datasets import load_dataset
            
            # Load dataset
            if config:
                dataset = load_dataset(dataset_name, config)
            else:
                dataset = load_dataset(dataset_name)
            
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Save dataset info
            dataset_info = {
                "name": dataset_name,
                "config": config,
                "splits": list(dataset.keys()),
                "downloaded_at": datetime.now().isoformat(),
                "source": "huggingface"
            }
            
            with open(target_dir / "dataset_info.json", 'w') as f:
                json.dump(dataset_info, f, indent=2)
            
            # Save each split
            for split_name, split_data in dataset.items():
                split_dir = target_dir / split_name
                split_dir.mkdir(exist_ok=True)
                
                # Convert to pandas and save as CSV
                df = split_data.to_pandas()
                df.to_csv(split_dir / f"{split_name}.csv", index=False)
                
                logger.info(f"Saved {split_name} split with {len(df)} samples")
            
            logger.info(f"Successfully downloaded {dataset_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {dataset_name}: {e}")
            return False
    
    def create_manual_dataset_placeholder(self, dataset_name: str, target_dir: Path, dataset_info: Dict) -> bool:
        """Create placeholder for datasets that need manual download"""
        try:
            logger.info(f"Creating placeholder for {dataset_name}...")
            
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Create instructions file
            instructions_file = target_dir / "DOWNLOAD_INSTRUCTIONS.md"
            instructions = f"""# Download {dataset_name} Manually

This dataset needs to be downloaded manually.

## Dataset Info:
- Name: {dataset_name}
- Description: {dataset_info['description']}
- Expected samples: {dataset_info['expected_samples']}
- Source: {dataset_info.get('url', 'Manual download required')}

## Steps:
1. Visit the source URL or search for the dataset
2. Download the dataset files
3. Extract to this directory
4. Ensure you have train/ and test/ folders with data files

## Expected Structure:
```
{dataset_name}/
├── train/
│   ├── data.csv (or similar)
│   └── labels.csv (if separate)
├── test/
│   ├── data.csv (or similar)
│   └── labels.csv (if separate)
└── dataset_info.json (will be created after download)
```

## After Download:
- Place train/test data in respective folders
- Update dataset_info.json with actual counts
- Ensure data is in CSV or JSON format
"""
            
            with open(instructions_file, 'w') as f:
                f.write(instructions)
            
            # Create placeholder structure
            (target_dir / "train").mkdir(exist_ok=True)
            (target_dir / "test").mkdir(exist_ok=True)
            
            # Create placeholder dataset info
            placeholder_info = {
                "name": dataset_name,
                "status": "placeholder_created",
                "created_at": datetime.now().isoformat(),
                "instructions": "See DOWNLOAD_INSTRUCTIONS.md"
            }
            
            with open(target_dir / "dataset_info.json", 'w') as f:
                json.dump(placeholder_info, f, indent=2)
            
            logger.info(f"Created placeholder for {dataset_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create placeholder for {dataset_name}: {e}")
            return False
    
    def download_dataset(self, category: str, dataset_name: str, dataset_info: Dict) -> bool:
        """Download a specific dataset"""
        target_dir = self.raw_datasets_dir / category / dataset_name
        
        if dataset_info["source"] == "huggingface":
            return self.download_huggingface_dataset(
                dataset_info["hf_name"],
                target_dir,
                dataset_info.get("config")
            )
        elif dataset_info["source"] == "manual":
            return self.create_manual_dataset_placeholder(
                dataset_name,
                target_dir,
                dataset_info
            )
        else:
            logger.warning(f"Unknown source for {dataset_name}: {dataset_info['source']}")
            return False
    
    def download_all_datasets(self):
        """Download all working datasets"""
        logger.info("🚀 Starting Simple Dataset Download Pipeline")
        
        success_count = 0
        total_count = 0
        
        for category, datasets in self.working_datasets.items():
            logger.info(f"📁 Processing category: {category}")
            
            for dataset_name, dataset_info in datasets.items():
                total_count += 1
                logger.info(f"📥 Downloading {dataset_name}...")
                
                if self.download_dataset(category, dataset_name, dataset_info):
                    success_count += 1
                    logger.info(f"✅ Successfully processed {dataset_name}")
                else:
                    logger.error(f"❌ Failed to process {dataset_name}")
                
                # Add delay to avoid overwhelming servers
                import time
                time.sleep(1)
        
        logger.info(f"🎉 Download completed! {success_count}/{total_count} datasets processed successfully")
        return success_count, total_count
    
    def create_dataset_summary(self):
        """Create updated dataset summary after downloads"""
        logger.info("📊 Creating updated dataset summary...")
        
        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_datasets": 0,
            "ready_datasets": 0,
            "placeholder_datasets": 0,
            "failed_datasets": 0,
            "categories_covered": set(),
            "estimated_samples": 0,
            "dataset_details": []
        }
        
        for category_dir in self.raw_datasets_dir.iterdir():
            if category_dir.is_dir():
                for dataset_dir in category_dir.iterdir():
                    if dataset_dir.is_dir():
                        summary["total_datasets"] += 1
                        
                        # Check if dataset has data
                        if self._has_valid_data(dataset_dir):
                            summary["ready_datasets"] += 1
                            summary["categories_covered"].add(category_dir.name)
                            
                            # Get sample count
                            sample_count = self._count_samples(dataset_dir)
                            summary["estimated_samples"] += sample_count
                            
                            # Get dataset info
                            dataset_info = self._get_dataset_info(dataset_dir)
                            summary["dataset_details"].append(dataset_info)
                        elif self._is_placeholder(dataset_dir):
                            summary["placeholder_datasets"] += 1
                            summary["categories_covered"].add(category_dir.name)
                        else:
                            summary["failed_datasets"] += 1
        
        summary["categories_covered"] = list(summary["categories_covered"])
        
        # Save summary
        summary_file = self.base_dir / "simple_dataset_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Dataset summary saved to {summary_file}")
        return summary
    
    def _has_valid_data(self, dataset_dir: Path) -> bool:
        """Check if dataset directory has valid data"""
        # Look for common data files
        data_files = list(dataset_dir.rglob("*.json")) + list(dataset_dir.rglob("*.csv")) + \
                    list(dataset_dir.rglob("*.arrow")) + list(dataset_dir.rglob("*.parquet"))
        
        # Look for image files
        image_files = list(dataset_dir.rglob("*.jpg")) + list(dataset_dir.rglob("*.png")) + \
                     list(dataset_dir.rglob("*.jpeg"))
        
        return len(data_files) > 0 or len(image_files) > 0
    
    def _is_placeholder(self, dataset_dir: Path) -> bool:
        """Check if dataset directory is a placeholder"""
        instructions_file = dataset_dir / "DOWNLOAD_INSTRUCTIONS.md"
        return instructions_file.exists()
    
    def _count_samples(self, dataset_dir: Path) -> int:
        """Estimate number of samples in dataset"""
        data_files = list(dataset_dir.rglob("*.json")) + list(dataset_dir.rglob("*.csv"))
        image_files = list(dataset_dir.rglob("*.jpg")) + list(dataset_dir.rglob("*.png"))
        
        return len(data_files) + len(image_files)
    
    def _get_dataset_info(self, dataset_dir: Path) -> Dict:
        """Get information about a dataset"""
        info_file = dataset_dir / "dataset_info.json"
        
        if info_file.exists():
            try:
                with open(info_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Fallback info
        return {
            "name": dataset_dir.name,
            "path": str(dataset_dir),
            "category": dataset_dir.parent.name,
            "status": "downloaded"
        }
    
    def run_full_pipeline(self):
        """Run the complete download pipeline"""
        logger.info("🚀 Starting Simple Dataset Download Pipeline")
        
        # Step 1: Download all datasets
        success_count, total_count = self.download_all_datasets()
        
        # Step 2: Create summary
        summary = self.create_dataset_summary()
        
        # Step 3: Final report
        final_report = {
            "pipeline_completed_at": datetime.now().isoformat(),
            "download_results": {
                "success": success_count,
                "total": total_count,
                "success_rate": f"{(success_count/total_count)*100:.1f}%"
            },
            "dataset_summary": summary
        }
        
        # Save final report
        report_file = self.base_dir / "simple_download_report.json"
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=2)
        
        logger.info("🎉 Simple Dataset Download Pipeline completed!")
        logger.info(f"Final report saved to {report_file}")
        
        return final_report

if __name__ == "__main__":
    downloader = SimpleDatasetDownloader()
    downloader.run_full_pipeline()

