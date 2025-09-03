# Vision Transformer (ViT) Training for Document Classification

This directory contains the Vision Transformer training setup for classifying document images into different categories (resume, education, insurance, legal).

## Overview

The ViT model is designed to classify synthetic document images into four main categories:
- **Resume/Employment**: Job applications, CVs, resumes
- **Education**: Academic documents, certificates, transcripts
- **Insurance**: Policy documents, claims, insurance forms
- **Legal**: Contracts, court documents, legal agreements

## Directory Structure

```
ViT/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── ViT_Training_Notebook.ipynb  # Main training notebook
├── models/                   # Saved model files
├── data/                     # Processed dataset metadata
├── notebooks/                # Additional notebooks
├── scripts/                  # Utility scripts
│   └── prepare_data.py       # Data preparation script
└── artifacts/                # Training artifacts and checkpoints
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Data

Run the data preparation script to organize the synthetic image datasets:

```bash
cd scripts
python prepare_data.py
```

This will:
- Scan the synthetic image datasets
- Create metadata files
- Generate CSV files for easy loading
- Create a sample dataset for testing

### 3. Training

Open the Jupyter notebook and run the training:

```bash
jupyter notebook ViT_Training_Notebook.ipynb
```

## Model Architecture

The ViT model uses:
- **Base Model**: `google/vit-base-patch16-224`
- **Image Size**: 224x224 pixels
- **Patch Size**: 16x16 pixels
- **Number of Classes**: 4 (document categories)

## Training Features

- **Transfer Learning**: Pre-trained on ImageNet
- **Data Augmentation**: Random crops, flips, rotations, color jittering
- **Early Stopping**: Based on validation F1 score
- **Learning Rate Scheduling**: Linear warmup + decay
- **Gradient Clipping**: Prevents exploding gradients
- **Mixed Precision**: Faster training with less memory

## Configuration

Key training parameters in the notebook:

```python
CONFIG = {
    'model_name': 'google/vit-base-patch16-224',
    'image_size': 224,
    'batch_size': 32,
    'epochs': 20,
    'learning_rate': 2e-5,
    'weight_decay': 0.01,
    'warmup_ratio': 0.1,
    'patience': 5,
    'gradient_clip': 1.0,
    'use_augmentation': True
}
```

## Usage Examples

### Training

1. Open the notebook
2. Run all cells sequentially
3. Monitor training progress
4. Save the best model

### Inference

```python
from PIL import Image
import torch
from transformers import ViTForImageClassification
import torch.nn.functional as F

# Load trained model
model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')
checkpoint = torch.load('artifacts/vit_model.pt')
model.load_state_dict(checkpoint['model_state_dict'])

# Predict on new image
image = Image.open('path/to/document.png').convert('RGB')
# ... preprocessing ...
prediction = model(image_tensor)
```

### Deployment

The training notebook automatically creates:
- Deployment-ready model file
- Label mapping
- Inference script
- Model metadata

## Performance Metrics

The model is evaluated using:
- **Accuracy**: Overall correct predictions
- **F1 Score**: Macro-averaged F1 score
- **Per-class metrics**: Precision, recall, F1 for each category

## Data Sources

The training data comes from synthetic image datasets:
- `data/training_data/processed_datasets/synthetic_images/`
  - `resume_employment/`
  - `education/`
  - `insurance/`
  - `legal/`

## Troubleshooting

### Common Issues

1. **Out of Memory**: Reduce batch size or image size
2. **Slow Training**: Use GPU acceleration, reduce data augmentation
3. **Poor Performance**: Check data quality, adjust learning rate

### Performance Tips

- Use GPU for faster training
- Start with sample dataset for testing
- Monitor validation metrics
- Use early stopping to prevent overfitting

## Model Files

After training, the following files are created:

- `artifacts/vit_model.pt`: Best model checkpoint
- `artifacts/label_map.json`: Class label mapping
- `artifacts/training_history.json`: Training metrics
- `artifacts/vit_deployment_model.pt`: Deployment-ready model
- `artifacts/deployment_script.py`: Inference script

## Next Steps

1. **Hyperparameter Tuning**: Experiment with different learning rates, architectures
2. **Data Augmentation**: Add more augmentation techniques
3. **Ensemble Methods**: Combine multiple models
4. **Real-time Deployment**: Integrate with web application
5. **Model Compression**: Optimize for production use

## Contributing

To improve the ViT training setup:
1. Test with different architectures
2. Add new data augmentation techniques
3. Implement advanced training strategies
4. Optimize for specific use cases
