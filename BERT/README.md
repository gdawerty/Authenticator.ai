# BERT Document Classification - Clean Structure

## 📁 Folder Structure

```
clean_bert/
├── notebooks/           # Jupyter notebooks
│   ├── BERT_Training_Notebook.ipynb      # Original training notebook
│   └── BERT_Training_Updated.ipynb       # Updated for new categories
├── scripts/             # Python scripts
│   ├── test_predict.py                   # Test prediction function
│   └── recategorize_data_complete.py     # Data recategorization script
├── data/                # Training data
│   └── recategorized_data_complete/      # 1.5M samples, 52 subcategories
├── models/              # Trained models
│   └── hierarchical_artifacts/           # Current trained model
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## 🚀 Quick Start

### 1. Test Current Model
```bash
cd scripts
python3 test_predict.py
```

### 2. Train on New Data
```bash
cd notebooks
# Open BERT_Training_Updated.ipynb
# Update paths to use data/recategorized_data_complete/
```

### 3. Recategorize Data
```bash
cd scripts
python3 recategorize_data_complete.py
```

## 📊 Current Model Status

- **Model**: Trained on hierarchical data (5 categories)
- **Categories**: Educational_Transcript, Financial_Insurance Document, Legal_Contract, Legal_Legal Document, Other_Unknown Document
- **Data**: 51K samples

## 🎯 New Data Available

- **Total Samples**: 1.5M+
- **Categories**: 52 granular subcategories
- **Main Categories**: Education, Finance, Medical, Supply Chain, Other

## 📈 Next Steps

1. **Retrain on new data** for better classification
2. **Use granular categories** for specific document types
3. **Add medical/supply chain data** when available

## 🔧 Dependencies

Install requirements:
```bash
pip install -r requirements.txt
```
