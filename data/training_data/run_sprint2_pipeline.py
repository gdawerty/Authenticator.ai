#!/usr/bin/env python3
"""
Main Execution Script for Authentia.ai Sprint 2 Data Pipeline
Runs the complete data processing pipeline from start to finish
"""

import os
import sys
import logging
from pathlib import Path
import argparse
from datetime import datetime

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from sprint2_data_orchestrator import Sprint2DataOrchestrator
from data_quality_checker import DataQualityChecker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'sprint2_pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Run Authentia.ai Sprint 2 Data Pipeline')
    parser.add_argument('--base-dir', type=str, 
                       default="/Users/prathamsaurabh/Authenticator.ai/data/training_data",
                       help='Base directory for the project')
    parser.add_argument('--skip-synthetic', action='store_true',
                       help='Skip synthetic data generation')
    parser.add_argument('--skip-cleaning', action='store_true',
                       help='Skip data cleaning step')
    parser.add_argument('--target-samples', type=int, default=1000,
                       help='Target samples per category for synthetic data')
    parser.add_argument('--test-size', type=float, default=0.15,
                       help='Test set size (default: 0.15)')
    parser.add_argument('--val-size', type=float, default=0.15,
                       help='Validation set size (default: 0.15)')
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting Authentia.ai Sprint 2 Data Pipeline")
    logger.info(f"Base directory: {args.base_dir}")
    logger.info(f"Target samples per category: {args.target_samples}")
    logger.info(f"Test size: {args.test_size}, Validation size: {args.val_size}")
    
    try:
        # Step 1: Initialize the data orchestrator
        logger.info("📊 Initializing Data Orchestrator...")
        orchestrator = Sprint2DataOrchestrator(base_dir=args.base_dir)
        
        # Step 2: Check current dataset status
        logger.info("🔍 Checking current dataset status...")
        status = orchestrator.get_dataset_status()
        logger.info(f"Current status: {status}")
        
        # Step 3: Generate synthetic data (if not skipped)
        if not args.skip_synthetic:
            logger.info("🎨 Generating synthetic data...")
            synthetic_data = orchestrator.generate_synthetic_data(
                target_samples_per_category=args.target_samples
            )
            logger.info(f"Generated {len(synthetic_data['text'])} text categories and {len(synthetic_data['image'])} image categories")
        else:
            logger.info("⏭️ Skipping synthetic data generation")
            synthetic_data = {"text": {}, "image": {}}
        
        # Step 4: Create train/validation/test splits
        logger.info("✂️ Creating train/validation/test splits...")
        splits = orchestrator.create_train_val_test_splits(
            test_size=args.test_size,
            val_size=args.val_size
        )
        
        # Step 5: Data cleaning (if not skipped)
        if not args.skip_cleaning:
            logger.info("🧹 Starting data cleaning pipeline...")
            checker = DataQualityChecker(base_dir=args.base_dir)
            
            # Find files to clean
            processed_dir = Path(args.base_dir) / "processed_datasets"
            splits_dir = Path(args.base_dir) / "model_splits"
            
            # Clean synthetic data
            synthetic_text_files = list(processed_dir.rglob("*_synthetic.csv"))
            synthetic_image_files = list(processed_dir.rglob("*_metadata.csv"))
            
            if synthetic_text_files or synthetic_image_files:
                logger.info("Cleaning synthetic data...")
                cleaned_synthetic = checker.run_full_cleaning_pipeline(
                    text_files=[str(f) for f in synthetic_text_files],
                    image_files=[str(f) for f in synthetic_image_files]
                )
                logger.info(f"Cleaned {len(cleaned_synthetic)} synthetic datasets")
            
            # Clean split data
            split_text_files = list(splits_dir.rglob("*.csv"))
            if split_text_files:
                logger.info("Cleaning split data...")
                cleaned_splits = checker.run_full_cleaning_pipeline(
                    text_files=[str(f) for f in split_text_files]
                )
                logger.info(f"Cleaned {len(cleaned_splits)} split datasets")
        else:
            logger.info("⏭️ Skipping data cleaning step")
        
        # Step 6: Generate final summary
        logger.info("📋 Generating final pipeline summary...")
        final_summary = {
            "pipeline_completed_at": datetime.now().isoformat(),
            "pipeline_version": "Sprint 2 v1.0",
            "initial_status": status,
            "synthetic_data_generated": len(synthetic_data["text"]) + len(synthetic_data["image"]),
            "final_splits": {
                "text": {
                    "train": len(splits["text"]["train"]),
                    "val": len(splits["text"]["val"]),
                    "test": len(splits["text"]["test"]),
                    "total": len(splits["text"]["train"]) + len(splits["text"]["val"]) + len(splits["text"]["test"])
                },
                "image": {
                    "train": len(splits["image"]["train"]),
                    "val": len(splits["image"]["val"]),
                    "test": len(splits["image"]["test"]),
                    "total": len(splits["image"]["train"]) + len(splits["image"]["val"]) + len(splits["image"]["test"])
                }
            },
            "pipeline_steps_completed": [
                "Dataset status check",
                "Synthetic data generation" if not args.skip_synthetic else "Synthetic data generation (skipped)",
                "Train/val/test splits creation",
                "Data cleaning" if not args.skip_cleaning else "Data cleaning (skipped)"
            ]
        }
        
        # Save final summary
        summary_file = Path(args.base_dir) / "sprint2_pipeline_summary.json"
        import json
        with open(summary_file, 'w') as f:
            json.dump(final_summary, f, indent=2)
        
        logger.info("🎉 Sprint 2 Data Pipeline completed successfully!")
        logger.info(f"Final summary saved to {summary_file}")
        
        # Print summary to console
        print("\n" + "="*60)
        print("🎉 SPRINT 2 DATA PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"📊 Total Text Samples: {final_summary['final_splits']['text']['total']}")
        print(f"🖼️  Total Image Samples: {final_summary['final_splits']['image']['total']}")
        print(f"🎨 Synthetic Data Categories: {final_summary['synthetic_data_generated']}")
        print(f"📁 Summary saved to: {summary_file}")
        print("="*60)
        print("\n🚀 Ready for model training!")
        print("Next steps:")
        print("1. Review the data splits in model_splits/")
        print("2. Check quality reports in cleaned_datasets/")
        print("3. Start training BERT and ViT models")
        print("4. Implement the /classify API endpoint")
        
        return final_summary
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed with error: {e}")
        logger.error("Stack trace:", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

