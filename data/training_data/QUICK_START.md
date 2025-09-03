# 🚀 Authentia.ai Sprint 2 Data Pipeline - Quick Start Guide

## 🎯 What This Pipeline Does

This pipeline prepares your data for **Sprint 2** of Authentia.ai, which focuses on **document classification** using:
- **BERT** for text classification
- **ViT** for image classification

The pipeline will:
1. ✅ Check your existing datasets
2. 🎨 Generate synthetic data to fill gaps
3. ✂️ Create train/validation/test splits (70/15/15)
4. 🧹 Clean and validate data quality
5. 📊 Generate comprehensive reports

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies
```bash
cd /Users/prathamsaurabh/Authenticator.ai/data/training_data
pip install -r data_processing_requirements.txt
```

### 2. Run the Full Pipeline
```bash
python run_sprint2_pipeline.py
```

This will:
- Generate 1000 synthetic samples per category
- Create balanced train/val/test splits
- Clean and validate all data
- Save everything to organized directories

### 3. Customize (Optional)
```bash
# Generate more synthetic data
python run_sprint2_pipeline.py --target-samples 2000

# Skip synthetic data generation (use only existing data)
python run_sprint2_pipeline.py --skip-synthetic

# Skip data cleaning (use only basic processing)
python run_sprint2_pipeline.py --skip-cleaning

# Custom split ratios
python run_sprint2_pipeline.py --test-size 0.2 --val-size 0.1
```

## 📁 Output Structure

After running the pipeline, you'll have:

```
training_data/
├── processed_datasets/          # Raw synthetic data
│   ├── synthetic_text/         # Generated text samples
│   └── synthetic_images/       # Generated image samples
├── cleaned_datasets/           # Cleaned and validated data
│   ├── quality_reports/        # Data quality analysis
│   └── cleaned_*.csv          # Cleaned datasets
├── model_splits/              # Ready for training
│   ├── text/
│   │   ├── train.csv
│   │   ├── val.csv
│   │   └── test.csv
│   └── image/
│       ├── train.csv
│       ├── val.csv
│       └── test.csv
└── sprint2_pipeline_summary.json  # Complete pipeline summary
```

## 🎨 Synthetic Data Generated

The pipeline creates realistic synthetic data for:

### **High Priority Categories**
- **Education**: Transcripts, Report Cards, Attendance Logs, Immunization Forms
- **Insurance**: Accident Claims, Policy Forms, Invoices, Medical Records

### **Medium Priority Categories**
- **Legal**: NDAs, Contracts, Leases, Service Agreements
- **Resume/Employment**: Resumes, Cover Letters, Reference Letters, Certifications

### **Low Priority Categories**
- **Other**: General Documents, Forms, Letters

## 🔍 Data Quality Features

- **PII Detection & Masking**: Automatically detects and masks personal information
- **Duplicate Removal**: Removes exact and near-duplicate samples
- **Quality Filtering**: Filters out low-quality text and images
- **Category Validation**: Ensures consistent category labeling
- **Stratified Splits**: Maintains category balance across splits

## 📊 What You Get

### **Text Data**
- Clean, normalized text content
- PII-masked for privacy
- Balanced category distribution
- Quality metrics and reports

### **Image Data**
- Validated image files
- Consistent sizing and format
- Perceptual hash deduplication
- Quality assessment reports

## 🚀 Next Steps After Pipeline

1. **Review Data Quality Reports**
   - Check `cleaned_datasets/quality_reports/`
   - Ensure category balance looks good

2. **Start Model Training**
   - Use `model_splits/text/` for BERT training
   - Use `model_splits/image/` for ViT training

3. **Build Classification API**
   - Implement `/classify` endpoint
   - Add confidence scoring

4. **Prepare for Sprint 3**
   - VLA/VLM authenticity detection
   - Paired text-image datasets

## 🆘 Troubleshooting

### **Common Issues**

**Missing Dependencies**
```bash
pip install --upgrade pip
pip install -r data_processing_requirements.txt
```

**Permission Errors**
```bash
chmod +x run_sprint2_pipeline.py
```

**Memory Issues**
```bash
# Reduce synthetic data size
python run_sprint2_pipeline.py --target-samples 500
```

**Dataset Not Found**
- Check that your `raw_datasets/` directory exists
- Ensure datasets have valid data files

### **Get Help**

- Check the log files: `sprint2_pipeline_*.log`
- Review the pipeline summary: `sprint2_pipeline_summary.json`
- Check individual quality reports in `cleaned_datasets/`

## 🎯 Success Metrics

Your pipeline is successful when you have:

- ✅ **Text Data**: 5,000+ samples across all categories
- ✅ **Image Data**: 2,500+ samples across all categories
- ✅ **Balanced Splits**: 70/15/15 distribution maintained
- ✅ **Quality Reports**: All datasets pass quality checks
- ✅ **Category Coverage**: All 5 main categories represented

## 🚀 Ready to Go!

Run the pipeline and get your data ready for **Sprint 2** model training. This will give you a solid foundation for building your document classification engine!

---

**Need help?** Check the logs and quality reports for detailed information about what happened during processing.

