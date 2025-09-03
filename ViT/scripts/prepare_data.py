#!/usr/bin/env python3
"""
Data preparation script for ViT training on document images.
Organizes synthetic image datasets into a structured format.
"""

import os
import json
import shutil
from pathlib import Path
from collections import defaultdict
import pandas as pd

def prepare_vit_data():
    """Prepare data for ViT training"""
    
    # Configuration
    data_root = Path("../data/training_data/processed_datasets/synthetic_images")
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    # Document categories
    categories = ['resume_employment', 'education', 'insurance', 'legal']
    
    # Statistics
    stats = {
        'total_images': 0,
        'category_counts': defaultdict(int),
        'image_paths': []
    }
    
    print("Preparing ViT training data...")
    print(f"Source: {data_root}")
    print(f"Output: {output_dir}")
    
    # Process each category
    for category in categories:
        category_path = data_root / category
        if not category_path.exists():
            print(f"Warning: Category {category} not found at {category_path}")
            continue
            
        print(f"\nProcessing category: {category}")
        
        # Find all image files
        image_files = list(category_path.rglob('*.png')) + list(category_path.rglob('*.jpg'))
        
        if not image_files:
            print(f"Warning: No images found in {category}")
            continue
            
        print(f"Found {len(image_files)} images")
        
        # Update statistics
        stats['category_counts'][category] = len(image_files)
        stats['total_images'] += len(image_files)
        
        # Add image paths to list
        for img_path in image_files:
            stats['image_paths'].append({
                'path': str(img_path),
                'category': category,
                'filename': img_path.name
            })
    
    # Create metadata file
    metadata = {
        'total_images': stats['total_images'],
        'categories': list(stats['category_counts'].keys()),
        'category_counts': dict(stats['category_counts']),
        'image_paths': stats['image_paths']
    }
    
    with open(output_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Create CSV file for easy loading
    df = pd.DataFrame(stats['image_paths'])
    df.to_csv(output_dir / 'image_dataset.csv', index=False)
    
    print(f"\nData preparation completed!")
    print(f"Total images: {stats['total_images']}")
    print(f"Categories: {list(stats['category_counts'].keys())}")
    print(f"Category distribution:")
    for category, count in stats['category_counts'].items():
        print(f"  {category}: {count} images")
    
    print(f"\nFiles created:")
    print(f"  - {output_dir / 'metadata.json'}")
    print(f"  - {output_dir / 'image_dataset.csv'}")

def create_sample_dataset(sample_size=100):
    """Create a smaller sample dataset for testing"""
    
    data_root = Path("data")
    metadata_path = data_root / "metadata.json"
    
    if not metadata_path.exists():
        print("Error: Run prepare_vit_data() first")
        return
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    # Sample images from each category
    sample_data = []
    images_per_category = sample_size // len(metadata['categories'])
    
    for category in metadata['categories']:
        category_images = [img for img in metadata['image_paths'] if img['category'] == category]
        sampled = category_images[:images_per_category]
        sample_data.extend(sampled)
    
    # Save sample dataset
    sample_metadata = {
        'total_images': len(sample_data),
        'categories': metadata['categories'],
        'category_counts': {cat: len([img for img in sample_data if img['category'] == cat]) 
                           for cat in metadata['categories']},
        'image_paths': sample_data
    }
    
    with open(data_root / 'sample_metadata.json', 'w') as f:
        json.dump(sample_metadata, f, indent=2)
    
    df = pd.DataFrame(sample_data)
    df.to_csv(data_root / 'sample_dataset.csv', index=False)
    
    print(f"Sample dataset created with {len(sample_data)} images")

if __name__ == "__main__":
    # Prepare full dataset
    prepare_vit_data()
    
    # Create sample dataset for testing
    create_sample_dataset(sample_size=200)
