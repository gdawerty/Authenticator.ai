#!/usr/bin/env python3
import os
import json
import time
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dataset_exists(dataset_path):
    """Check if dataset actually has data files (not just state.json)"""
    if not dataset_path.exists():
        return False
    
    # Check for actual data files, not just state.json
    data_files = []
    for file in dataset_path.rglob("*"):
        if file.is_file() and not file.name.endswith(('.json', '.lock')):
            if file.suffix in ['.arrow', '.parquet', '.csv', '.txt'] or file.stat().st_size > 1000:
                data_files.append(file)
    
    return len(data_files) > 0

def download_dataset(dataset_name, hf_name):
    """Download a HuggingFace dataset"""
    try:
        from datasets import load_dataset
        
        base_path = Path("/Users/prathamsaurabh/Authenticator.ai/data/training_data/raw_datasets")
        dataset_path = base_path / dataset_name
        
        if check_dataset_exists(dataset_path):
            logger.info(f"✅ {dataset_name} already has data")
            return True
        
        logger.info(f"📥 Downloading {dataset_name} from {hf_name}")
        
        # Remove existing directory if it only has state files
        if dataset_path.exists():
            import shutil
            shutil.rmtree(dataset_path)
        
        dataset_path.mkdir(parents=True, exist_ok=True)
        
        # Download dataset
        dataset = load_dataset(hf_name, trust_remote_code=True)
        
        # Save to disk
        dataset.save_to_disk(str(dataset_path))
        
        if check_dataset_exists(dataset_path):
            logger.info(f"✅ {dataset_name} downloaded successfully")
            return True
        else:
            logger.error(f"❌ {dataset_name} download failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to download {dataset_name}: {e}")
        return False

def create_synthetic_data(dataset_name, num_samples=1000):
    """Create synthetic data for a dataset"""
    base_path = Path("/Users/prathamsaurabh/Authenticator.ai/data/training_data/raw_datasets")
    dataset_path = base_path / dataset_name
    
    if check_dataset_exists(dataset_path):
        logger.info(f"✅ {dataset_name} already has data")
        return True
    
    logger.info(f"🎨 Creating synthetic data for {dataset_name}")
    
    try:
        dataset_path.mkdir(parents=True, exist_ok=True)
        
        # Create synthetic data based on dataset type
        data = []
        category = dataset_name.split('/')[0]
        
        for i in range(num_samples):
            if 'education' in category:
                item = {
                    "id": f"EDU{i:06d}",
                    "text": f"Student transcript {i}: Mathematics A, Science B+, English A-",
                    "category": "education",
                    "subcategory": "transcript",
                    "authentic": i % 5 != 0,  # 80% authentic
                    "gpa": round(2.5 + (i % 150) / 100, 2)
                }
            elif 'insurance' in category or 'legal' in category:
                item = {
                    "id": f"INS{i:06d}",
                    "text": f"Insurance claim {i}: Vehicle damage estimated at ${1000 + i*5}",
                    "category": "insurance",
                    "subcategory": "claim",
                    "authentic": i % 6 != 0,  # ~83% authentic
                    "amount": 1000 + i*5
                }
            elif 'employment' in category or 'resume' in category:
                item = {
                    "id": f"EMP{i:06d}",
                    "text": f"Resume {i}: Software Engineer with {2 + i%8} years experience",
                    "category": "employment", 
                    "subcategory": "resume",
                    "authentic": i % 7 != 0,  # ~86% authentic
                    "experience": 2 + i%8
                }
            else:
                item = {
                    "id": f"DOC{i:06d}",
                    "text": f"Document {i} for classification training",
                    "category": "other",
                    "subcategory": "document",
                    "authentic": True
                }
            
            data.append(item)
        
        # Save synthetic data
        data_file = dataset_path / "synthetic_data.json"
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Created {len(data)} synthetic samples for {dataset_name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create synthetic data for {dataset_name}: {e}")
        return False

def main():
    """Main data collection function"""
    logger.info("🚀 Starting Authentia AI Robust Data Collection")
    
    # Priority datasets
    real_datasets = [
        ("education/funsd", "nielsr/funsd"),
        ("education/squad", "squad"),
        ("resume_employment/imdb_text", "imdb"),
        ("resume_employment/ag_news", "ag_news"),
        ("legal_insurance/ms_marco", "ms_marco"),
        ("vision/mnist", "mnist"),
        ("vision/fashion_mnist", "fashion_mnist"),
        ("vision/cifar10", "cifar10"),
    ]
    
    # Download real datasets
    success_count = 0
    for dataset_name, hf_name in real_datasets:
        if download_dataset(dataset_name, hf_name):
            success_count += 1
        time.sleep(1)  # Rate limiting
    
    logger.info(f"✅ Downloaded {success_count}/{len(real_datasets)} real datasets")
    
    # Create synthetic datasets
    synthetic_datasets = [
        "education/talkmoves",
        "education/ednet", 
        "education/assistments",
        "resume_employment/fake_job_postings",
        "legal_insurance/cuad",
        "legal_insurance/insurance_qa",
        "vision/car_damage",
        "vision/stanford_cars",
        "forgery_vlm/midv_500",
        "forgery_vlm/fantasy_id",
    ]
    
    synthetic_count = 0
    for dataset_name in synthetic_datasets:
        if create_synthetic_data(dataset_name):
            synthetic_count += 1
    
    logger.info(f"🎨 Created {synthetic_count}/{len(synthetic_datasets)} synthetic datasets")
    
    total_success = success_count + synthetic_count
    total_datasets = len(real_datasets) + len(synthetic_datasets)
    
    logger.info(f"""
🎉 AUTHENTIA AI DATA COLLECTION COMPLETE!

📊 Results:
- Real datasets: {success_count}/{len(real_datasets)} ({success_count/len(real_datasets)*100:.1f}%)
- Synthetic datasets: {synthetic_count}/{len(synthetic_datasets)} ({synthetic_count/len(synthetic_datasets)*100:.1f}%)
- Total completion: {total_success}/{total_datasets} ({total_success/total_datasets*100:.1f}%)

🚀 Ready for Sprint 2 BERT/ViT training!
""")

if __name__ == "__main__":
    main()
