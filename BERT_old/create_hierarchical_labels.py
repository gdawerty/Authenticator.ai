#!/usr/bin/env python3
"""
Create hierarchical labels for document classification
Maps document types to verticals and subcategories
"""

import pandas as pd
import json
import os

def create_hierarchical_mapping():
    """Create mapping from document types to verticals and subcategories"""
    
    # Define the hierarchical structure
    vertical_mapping = {
        'contract': {
            'vertical': 'Legal',
            'subcategory': 'Contract'
        },
        'insurance_claim': {
            'vertical': 'Financial', 
            'subcategory': 'Insurance Document'
        },
        'legal_document': {
            'vertical': 'Legal',
            'subcategory': 'Legal Document'
        },
        'transcript': {
            'vertical': 'Educational',
            'subcategory': 'Transcript'
        }
    }
    
    return vertical_mapping

def process_csv_with_hierarchy(input_file, output_file, text_col='cleaned_text', doc_type_col='document_type'):
    """Process CSV to add hierarchical labels"""
    
    print(f"📥 Loading {input_file}...")
    
    # Load data with only needed columns
    df = pd.read_csv(input_file, usecols=[text_col, doc_type_col], low_memory=False)
    
    print(f"📊 Original data shape: {df.shape}")
    
    # Convert to string and remove empty document types
    df[doc_type_col] = df[doc_type_col].astype(str)
    df = df.dropna(subset=[doc_type_col])
    df = df[df[doc_type_col].str.len() > 0]
    
    print(f"📊 After filtering: {df.shape}")
    
    # Create hierarchical mapping
    mapping = create_hierarchical_mapping()
    
    # Add vertical and subcategory columns
    df['vertical'] = df[doc_type_col].map(lambda x: mapping.get(x, {}).get('vertical', 'Other'))
    df['subcategory'] = df[doc_type_col].map(lambda x: mapping.get(x, {}).get('subcategory', 'Unknown Document'))
    
    # Create combined label for BERT training
    df['hierarchical_label'] = df['vertical'] + '_' + df['subcategory']
    
    # Save processed data
    df.to_csv(output_file, index=False)
    
    print(f"✅ Saved to {output_file}")
    
    # Print statistics
    print("\n📊 Vertical Distribution:")
    vertical_counts = df['vertical'].value_counts()
    for vertical, count in vertical_counts.items():
        print(f"  {vertical}: {count:,} documents")
    
    print("\n📊 Subcategory Distribution:")
    subcategory_counts = df['subcategory'].value_counts()
    for subcategory, count in subcategory_counts.items():
        print(f"  {subcategory}: {count:,} documents")
    
    print("\n📊 Hierarchical Label Distribution:")
    hierarchical_counts = df['hierarchical_label'].value_counts()
    for label, count in hierarchical_counts.items():
        print(f"  {label}: {count:,} documents")
    
    return df

def create_label_maps(df):
    """Create label mapping files"""
    
    # Vertical mapping
    verticals = sorted(df['vertical'].unique())
    vertical_map = {i: vertical for i, vertical in enumerate(verticals)}
    
    # Subcategory mapping
    subcategories = sorted(df['subcategory'].unique())
    subcategory_map = {i: subcategory for i, subcategory in enumerate(subcategories)}
    
    # Hierarchical mapping
    hierarchical_labels = sorted(df['hierarchical_label'].unique())
    hierarchical_map = {i: label for i, label in enumerate(hierarchical_labels)}
    
    # Save mappings
    mappings = {
        'vertical_map': vertical_map,
        'subcategory_map': subcategory_map,
        'hierarchical_map': hierarchical_map,
        'num_verticals': len(verticals),
        'num_subcategories': len(subcategories),
        'num_hierarchical': len(hierarchical_labels)
    }
    
    with open('hierarchical_label_maps.json', 'w') as f:
        json.dump(mappings, f, indent=2)
    
    print(f"\n📁 Saved label mappings to hierarchical_label_maps.json")
    print(f"📊 {len(verticals)} verticals, {len(subcategories)} subcategories, {len(hierarchical_labels)} hierarchical labels")
    
    return mappings

def main():
    """Main processing function"""
    
    # Process training data
    print("🚀 Processing training data...")
    train_df = process_csv_with_hierarchy(
        '../data/CLEANED/text_train.csv',
        'hierarchical_train.csv'
    )
    
    print("\n🚀 Processing validation data...")
    val_df = process_csv_with_hierarchy(
        '../data/CLEANED/text_val.csv', 
        'hierarchical_val.csv'
    )
    
    print("\n🚀 Processing test data...")
    test_df = process_csv_with_hierarchy(
        '../data/CLEANED/text_test.csv',
        'hierarchical_test.csv'
    )
    
    # Create label mappings
    print("\n🏷️ Creating label mappings...")
    all_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    mappings = create_label_maps(all_df)
    
    print("\n🎉 Hierarchical data processing complete!")
    print(f"📁 Files created:")
    print(f"  - hierarchical_train.csv")
    print(f"  - hierarchical_val.csv") 
    print(f"  - hierarchical_test.csv")
    print(f"  - hierarchical_label_maps.json")

if __name__ == "__main__":
    main()
