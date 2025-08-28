#!/usr/bin/env python3
"""
Dataset Downloader and Organizer for Authenticator.ai
Systematically downloads and organizes ML training datasets for ViT and BERT training
"""

import os
import sys
import json
import logging
import zipfile
import tarfile
from pathlib import Path
from typing import Dict, List, Optional
import shutil

# Optional imports - will be loaded when needed
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from datasets import load_dataset
    HAS_DATASETS = True
except ImportError:
    HAS_DATASETS = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatasetOrganizer:
    def __init__(self, base_dir: str = "/Users/prathamsaurabh/Authenticator.ai/data/training_data"):
        self.base_dir = Path(base_dir)
        self.raw_datasets_dir = self.base_dir / "raw_datasets"
        self.train_dir = self.base_dir / "train_70"
        self.validation_dir = self.base_dir / "validation_15"
        self.test_dir = self.base_dir / "test_15"
        
        # Dataset configuration
        self.datasets_config = {
            "general_document_classification": {
                "rvl_cdip": {
                    "source": "huggingface",
                    "dataset_name": "rvl_cdip",
                    "description": "RVL-CDIP: Document image classification"
                },
                "funsd": {
                    "source": "huggingface", 
                    "dataset_name": "nielsr/funsd",
                    "description": "FUNSD: Form Understanding in Noisy Scanned Documents"
                },
                "docformer": {
                    "source": "huggingface",
                    "dataset_name": "microsoft/docformer",
                    "description": "DocFormer: Document understanding dataset"
                },
                "doclaynet": {
                    "source": "huggingface",
                    "dataset_name": "ds4sd/DocLayNet",
                    "description": "DocLayNet: Document layout analysis"
                },
                "publaynet": {
                    "source": "huggingface",
                    "dataset_name": "pierreguillou/publaynet",
                    "description": "PubLayNet: Document layout analysis"
                },
                "cuad": {
                    "source": "huggingface",
                    "dataset_name": "cuad",
                    "description": "CUAD: Contract Understanding Atticus Dataset"
                },
                "cord_receipt": {
                    "source": "url",
                    "url": "https://github.com/clovaai/cord/releases/download/v1.0/CORD-1k.zip",
                    "description": "CORD: Consolidated Receipt Dataset"
                }
            },
            "k12_education": {
                "math_qa": {
                    "source": "huggingface",
                    "dataset_name": "math_qa",
                    "description": "Mathematical question answering"
                },
                "science_questions": {
                    "source": "huggingface",
                    "dataset_name": "sciq",
                    "description": "Science questions dataset"
                }
            },
            "vision_datasets": {
                "coco_text": {
                    "source": "url",
                    "url": "https://vision.cornell.edu/se3/coco-text/",
                    "description": "COCO-Text: Text detection in natural images"
                },
                "textocr": {
                    "source": "huggingface",
                    "dataset_name": "facebook/textocr",
                    "description": "TextOCR: Text recognition dataset"
                },
                "total_text": {
                    "source": "url", 
                    "url": "https://github.com/cs-chan/Total-Text-Dataset",
                    "description": "Total-Text: Curved text detection"
                }
            },
            "forgery_vlm": {
                "audeering_forgery": {
                    "source": "huggingface",
                    "dataset_name": "audeering/forgery_detection",
                    "description": "Document forgery detection dataset"
                }
            }
        }
    
    def download_huggingface_dataset(self, dataset_name: str, save_path: Path) -> bool:
        """Download dataset from HuggingFace"""
        if not HAS_DATASETS:
            logger.error("datasets library not installed. Run: pip install datasets")
            return False
            
        try:
            logger.info(f"Downloading HuggingFace dataset: {dataset_name}")
            from datasets import load_dataset
            dataset = load_dataset(dataset_name)
            
            # Save dataset to disk
            dataset.save_to_disk(str(save_path))
            logger.info(f"Successfully downloaded {dataset_name} to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {dataset_name}: {e}")
            return False
    
    def download_url_dataset(self, url: str, save_path: Path, description: str) -> bool:
        """Download dataset from URL"""
        if not HAS_REQUESTS:
            logger.error("requests library not installed. Run: pip install requests")
            return False
            
        try:
            import requests
            logger.info(f"Downloading {description} from {url}")
            
            # Create save directory
            save_path.mkdir(parents=True, exist_ok=True)
            
            # Download file
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            filename = url.split('/')[-1]
            file_path = save_path / filename
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract if it's an archive
            if filename.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(save_path)
                os.remove(file_path)  # Remove zip after extraction
            elif filename.endswith(('.tar.gz', '.tgz')):
                with tarfile.open(file_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(save_path)
                os.remove(file_path)  # Remove tar after extraction
            
            logger.info(f"Successfully downloaded {description} to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download from {url}: {e}")
            return False
    
    def download_category(self, category: str) -> None:
        """Download all datasets in a category"""
        if category not in self.datasets_config:
            logger.error(f"Unknown category: {category}")
            return
        
        category_datasets = self.datasets_config[category]
        logger.info(f"Starting download for category: {category}")
        
        for dataset_name, config in category_datasets.items():
            save_path = self.raw_datasets_dir / category / dataset_name
            save_path.mkdir(parents=True, exist_ok=True)
            
            if config["source"] == "huggingface":
                self.download_huggingface_dataset(config["dataset_name"], save_path)
            elif config["source"] == "url":
                self.download_url_dataset(config["url"], save_path, config["description"])
            else:
                logger.warning(f"Unknown source type: {config['source']} for {dataset_name}")
    
    def organize_for_training(self, category: str, dataset_name: str) -> None:
        """Organize downloaded dataset into train/validation/test splits"""
        source_path = self.raw_datasets_dir / category / dataset_name
        
        if not source_path.exists():
            logger.error(f"Dataset not found: {source_path}")
            return
        
        logger.info(f"Organizing {category}/{dataset_name} for training")
        
        # Create category folders in train/validation/test
        for split_dir in [self.train_dir, self.validation_dir, self.test_dir]:
            category_dir = split_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
        
        # TODO: Implement specific split logic based on dataset format
        # This will vary by dataset - some have predefined splits, others need to be created
        
        logger.info(f"Organized {category}/{dataset_name} for training")
    
    def get_dataset_info(self) -> Dict:
        """Get information about available datasets"""
        info = {}
        for category, datasets in self.datasets_config.items():
            info[category] = {}
            for dataset_name, config in datasets.items():
                dataset_path = self.raw_datasets_dir / category / dataset_name
                info[category][dataset_name] = {
                    "description": config["description"],
                    "source": config["source"],
                    "downloaded": dataset_path.exists(),
                    "path": str(dataset_path)
                }
        return info
    
    def list_available_categories(self) -> List[str]:
        """List all available dataset categories"""
        return list(self.datasets_config.keys())

def main():
    organizer = DatasetOrganizer()
    
    if len(sys.argv) < 2:
        print("Usage: python dataset_downloader.py <command> [args]")
        print("Commands:")
        print("  list-categories - List available dataset categories")
        print("  info - Show dataset information")
        print("  download <category> - Download all datasets in category")
        print("  download-all - Download all datasets")
        print("  organize <category> <dataset> - Organize dataset for training")
        return
    
    command = sys.argv[1]
    
    if command == "list-categories":
        categories = organizer.list_available_categories()
        print("Available categories:")
        for cat in categories:
            print(f"  - {cat}")
    
    elif command == "info":
        info = organizer.get_dataset_info()
        print(json.dumps(info, indent=2))
    
    elif command == "download":
        if len(sys.argv) < 3:
            print("Usage: python dataset_downloader.py download <category>")
            return
        category = sys.argv[2]
        organizer.download_category(category)
    
    elif command == "download-all":
        categories = organizer.list_available_categories()
        for category in categories:
            organizer.download_category(category)
    
    elif command == "organize":
        if len(sys.argv) < 4:
            print("Usage: python dataset_downloader.py organize <category> <dataset>")
            return
        category = sys.argv[2]
        dataset = sys.argv[3]
        organizer.organize_for_training(category, dataset)
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
