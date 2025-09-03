# 🚀 BERT Training Pipeline for Authentia.ai

Complete BERT training setup for document classification using your cleaned data.

## 📋 What's Included

- **`config.py`** - Training configuration and parameters
- **`data_processor.py`** - Data loading and preprocessing
- **`bert_model.py`** - BERT classifier model
- **`trainer.py`** - Training engine with metrics tracking
- **`train_bert.py`** - Main training script
- **`BERT_Training_Notebook.ipynb`** - Fixed & flexible BERT training notebook with advanced features
- **`requirements.txt`** - Python dependencies

## 🚀 Quick Start

### Option 1: Run Training Script (Recommended)
```bash
cd BERT
pip install -r requirements.txt
python train_bert.py
```

### Option 2: Use Jupyter Notebook
```bash
cd BERT
pip install -r requirements.txt
jupyter notebook BERT_Training_Notebook.ipynb
```

## 📊 Your Data

The pipeline automatically loads your cleaned data from:
- `../data/CLEANED/text_train.csv` - 51,706 training samples
- `../data/CLEANED/text_val.csv` - 2,901 validation samples  
- `../data/CLEANED/text_test.csv` - 2,902 test samples

## 🎯 What Gets Trained

- **Model**: BERT-base-uncased with classification head
- **Task**: 6-category document classification
- **Categories**: Education, Insurance, Legal, Resume, Admin, Other
- **Input**: Cleaned, normalized text (max 256 tokens)
- **Output**: Category predictions with confidence scores
- **Features**: Early stopping, class weighting, flexible data loading, column name mapping, label encoding

## ⚙️ Training Configuration

- **Batch Size**: 16
- **Learning Rate**: 2e-5
- **Epochs**: 5
- **Warmup Steps**: 500
- **Max Length**: 512 tokens
- **Device**: Auto-detects CUDA/MPS/CPU

## 📈 What You Get

- **Trained Model**: `bert_output/best_model.pt`
- **Training Curves**: Loss and accuracy plots
- **Performance Metrics**: Classification report, confusion matrix
- **Checkpoints**: Saved every 2 epochs
- **Training History**: JSON file with all metrics

## 🔧 Customization

Edit `config.py` to modify:
- Model architecture
- Training parameters
- Data paths
- Output settings

## 🎉 Expected Results

With your 57K+ text samples, expect:
- **Training Time**: 15-30 minutes on M4 Pro
- **Validation Accuracy**: 85%+ after 5 epochs
- **Test Accuracy**: 80-90% depending on data quality

## 🚨 Troubleshooting

### Common Issues:
1. **CUDA out of memory**: Reduce batch size in config
2. **Data loading errors**: Check CSV file paths
3. **Import errors**: Install requirements.txt

### Performance Tips:
- Use MPS (Apple Silicon) for faster training
- Reduce max_length if memory is limited
- Increase batch_size if you have more memory

## 📁 Output Structure

```
BERT/
├── bert_output/
│   ├── best_model.pt          # Best model
│   ├── final_model.pt         # Final model
│   ├── training_curves.png    # Training visualization
│   ├── training_history.json  # Metrics history
│   └── checkpoint_*.pt        # Training checkpoints
```

## 🎯 Next Steps

1. **Train the model** using the script or notebook
2. **Evaluate performance** on test set
3. **Fine-tune hyperparameters** if needed
4. **Deploy for inference** on new documents
5. **Train ViT model** for image classification

---

**Ready to train? Just run `python train_bert.py` or open the Jupyter notebook!** 🚀
