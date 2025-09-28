"""
ViT Classification Service
Handles Vision Transformer model inference for document image classification
"""

import os
import json
import logging
from typing import Dict, Any, Union, List
import torch
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from transformers import ViTImageProcessor, ViTForImageClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Transformers not available. ViT classification will not work.")
    TRANSFORMERS_AVAILABLE = False
    ViTImageProcessor = None
    ViTForImageClassification = None

class ViTClassifier:
    """Vision Transformer classifier for document images"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or self._get_default_model_path()
        self.model = None
        self.processor = None
        self.label_map = {}
        self.id_to_label = {}
        self.device = self._get_device()
        
        if TRANSFORMERS_AVAILABLE:
            try:
                self._load_model()
                logger.info("ViT classifier initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ViT classifier: {e}")
        else:
            logger.error("Transformers not available - ViT classification disabled")
    
    def _get_default_model_path(self) -> str:
        """Get default model path"""
        return os.path.join(os.path.dirname(__file__), '../../ViT/vit_model_artifacts')
    
    def _get_device(self) -> torch.device:
        """Determine the best available device"""
        if torch.cuda.is_available():
            device = torch.device('cuda')
            logger.info("Using CUDA for ViT inference")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = torch.device('mps')
            logger.info("Using MPS for ViT inference")
        else:
            device = torch.device('cpu')
            logger.info("Using CPU for ViT inference")
        
        return device
    
    def _load_model(self):
        """Load the trained ViT model and processor (with fallback)"""
        try:
            logger.info(f"Loading ViT model from {self.model_path}")
            
            # Load label mappings
            label_map_path = os.path.join(self.model_path, 'label_map.json')
            id_to_label_path = os.path.join(self.model_path, 'id_to_label.json')
            
            if os.path.exists(label_map_path):
                with open(label_map_path, 'r') as f:
                    self.label_map = json.load(f)
                logger.info(f"Loaded label map: {self.label_map}")
            else:
                logger.warning(f"Label map not found at {label_map_path}")
                # Default mapping for 4 categories
                self.label_map = {'education': 0, 'insurance': 1, 'legal': 2, 'resume': 3}
            
            if os.path.exists(id_to_label_path):
                with open(id_to_label_path, 'r') as f:
                    id_to_label_data = json.load(f)
                    self.id_to_label = {int(k): v for k, v in id_to_label_data.items()}
                logger.info(f"Loaded id to label: {self.id_to_label}")
            else:
                # Create reverse mapping
                self.id_to_label = {v: k for k, v in self.label_map.items()}
            
            try:
                # Try to load the actual model
                self.processor = ViTImageProcessor.from_pretrained(self.model_path)
                self.model = ViTForImageClassification.from_pretrained(
                    self.model_path,
                    local_files_only=True
                )
                self.model.to(self.device)
                self.model.eval()
                logger.info("ViT model loaded successfully")
                
            except Exception as model_error:
                logger.warning(f"Could not load trained ViT model: {model_error}")
                logger.info("Using fallback pre-trained ViT model")
                
                # Fallback to pre-trained ViT
                self.processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
                self.model = ViTForImageClassification.from_pretrained(
                    'google/vit-base-patch16-224',
                    num_labels=len(self.label_map),
                    ignore_mismatched_sizes=True
                )
                self.model.to(self.device)
                self.model.eval()
                logger.info("Fallback ViT model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading ViT model: {e}")
            raise
    
    def _load_image(self, image_input: Union[str, bytes, Image.Image]) -> Image.Image:
        """
        Load image from various input types
        
        Args:
            image_input: Can be file path (str), image bytes, or PIL Image
            
        Returns:
            PIL Image object
        """
        if isinstance(image_input, str):
            # File path
            return Image.open(image_input).convert('RGB')
        elif isinstance(image_input, bytes):
            # Image bytes
            return Image.open(io.BytesIO(image_input)).convert('RGB')
        elif isinstance(image_input, Image.Image):
            # Already a PIL Image
            return image_input.convert('RGB')
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")
    
    def classify(self, image_input: Union[str, bytes, Image.Image]) -> Dict[str, Any]:
        """
        Classify an image using the ViT model
        
        Args:
            image_input: Image to classify (file path, bytes, or PIL Image)
            
        Returns:
            Dictionary containing classification results
        """
        if not TRANSFORMERS_AVAILABLE or self.model is None:
            return {
                'success': False,
                'error': 'ViT model not available',
                'top_prediction': {'category': 'unknown', 'confidence': 0.0}
            }
        
        try:
            # Load and preprocess image
            image = self._load_image(image_input)
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Process results
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)[0]
            
            # Get top prediction
            predicted_class_idx = logits.argmax(-1).item()
            confidence = probabilities[predicted_class_idx].item()
            
            # Map to label
            predicted_label = self.id_to_label.get(predicted_class_idx, 'unknown')
            
            # Get all predictions (top 3)
            top_k = min(3, len(probabilities))
            top_indices = torch.topk(probabilities, top_k).indices
            all_predictions = []
            
            for idx in top_indices:
                idx_val = idx.item()
                label = self.id_to_label.get(idx_val, f'class_{idx_val}')
                conf = probabilities[idx_val].item()
                all_predictions.append({
                    'category': label,
                    'confidence': conf,
                    'rank': len(all_predictions) + 1
                })
            
            return {
                'success': True,
                'top_prediction': {
                    'category': predicted_label,
                    'confidence': confidence,
                    'rank': 1
                },
                'all_predictions': all_predictions,
                'model_info': {
                    'model_type': 'ViT (Vision Transformer)',
                    'device': str(self.device),
                    'num_classes': len(self.label_map)
                }
            }
            
        except Exception as e:
            logger.error(f"Error during ViT classification: {e}")
            return {
                'success': False,
                'error': str(e),
                'top_prediction': {'category': 'unknown', 'confidence': 0.0}
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            'model_path': self.model_path,
            'device': str(self.device),
            'ready': self.model is not None,
            'label_map': self.label_map,
            'num_classes': len(self.label_map) if self.label_map else 0,
            'transformers_available': TRANSFORMERS_AVAILABLE
        }

# Global classifier instance
_vit_classifier = None

def get_vit_classifier() -> ViTClassifier:
    """Get or create global ViT classifier instance"""
    global _vit_classifier
    if _vit_classifier is None:
        _vit_classifier = ViTClassifier()
    return _vit_classifier

def classify_image(image_input: Union[str, bytes, Image.Image]) -> Dict[str, Any]:
    """
    Classify an image using ViT
    
    Args:
        image_input: Image to classify
        
    Returns:
        Classification results dictionary
    """
    classifier = get_vit_classifier()
    return classifier.classify(image_input)

def get_model_info() -> Dict[str, Any]:
    """Get ViT model information"""
    classifier = get_vit_classifier()
    return classifier.get_model_info()


