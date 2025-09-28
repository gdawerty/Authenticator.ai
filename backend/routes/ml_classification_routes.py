"""
ML Classification Routes
API endpoints for BERT and ViT model inference
"""

from flask import Blueprint, request, jsonify
from werkzeug.datastructures import FileStorage
import logging

logger = logging.getLogger(__name__)

# Create blueprint
ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')

@ml_bp.route('/health', methods=['GET'])
def health_check():
    """Check ML services health"""
    try:
        from ..services.bert_classification_service import get_model_info as get_bert_info
        from ..services.vit_classification_service import get_model_info as get_vit_info
        
        bert_info = get_bert_info()
        vit_info = get_vit_info()
        
        return jsonify({
            'status': 'healthy',
            'services': {
                'bert': {
                    'ready': bert_info.get('ready', False),
                    'device': bert_info.get('device', 'unknown')
                },
                'vit': {
                    'ready': vit_info.get('ready', False),
                    'device': vit_info.get('device', 'unknown')
                }
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@ml_bp.route('/models/info', methods=['GET'])
def models_info():
    """Get detailed information about loaded models"""
    try:
        from ..services.bert_classification_service import get_model_info as get_bert_info
        from ..services.vit_classification_service import get_model_info as get_vit_info
        
        return jsonify({
            'bert': get_bert_info(),
            'vit': get_vit_info()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ml_bp.route('/bert/classify', methods=['POST'])
def bert_classify():
    """Classify text using BERT"""
    try:
        from ..services.bert_classification_service import classify_text
        
        # Get text from request
        if request.is_json:
            data = request.get_json()
            text = data.get('text', '')
        else:
            text = request.form.get('text', '')
        
        if not text or not text.strip():
            return jsonify({'error': 'No text provided'}), 400
        
        # Classify
        result = classify_text(text)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"BERT classification error: {e}")
        return jsonify({'error': str(e)}), 500

@ml_bp.route('/bert/classify-batch', methods=['POST'])
def bert_classify_batch():
    """Classify multiple texts using BERT"""
    try:
        from ..services.bert_classification_service import classify_text
        
        data = request.get_json()
        texts = data.get('texts', [])
        
        if not texts:
            return jsonify({'error': 'No texts provided'}), 400
        
        results = []
        for i, text in enumerate(texts):
            if text and text.strip():
                result = classify_text(text)
                result['index'] = i
                results.append(result)
            else:
                results.append({
                    'index': i,
                    'success': False,
                    'error': 'Empty text'
                })
        
        return jsonify({'results': results})
        
    except Exception as e:
        logger.error(f"BERT batch classification error: {e}")
        return jsonify({'error': str(e)}), 500

@ml_bp.route('/vit/classify', methods=['POST'])
def vit_classify():
    """Classify image using ViT"""
    try:
        from ..services.vit_classification_service import classify_image
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read image bytes
        image_bytes = file.read()
        if not image_bytes:
            return jsonify({'error': 'Empty file'}), 400
        
        # Classify
        result = classify_image(image_bytes)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"ViT classification error: {e}")
        return jsonify({'error': str(e)}), 500

@ml_bp.route('/vit/classify-batch', methods=['POST'])
def vit_classify_batch():
    """Classify multiple images using ViT"""
    try:
        from ..services.vit_classification_service import classify_image
        
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No files selected'}), 400
        
        results = []
        for i, file in enumerate(files):
            if file.filename != '':
                try:
                    image_bytes = file.read()
                    if image_bytes:
                        result = classify_image(image_bytes)
                        result['index'] = i
                        result['filename'] = file.filename
                        results.append(result)
                    else:
                        results.append({
                            'index': i,
                            'filename': file.filename,
                            'success': False,
                            'error': 'Empty file'
                        })
                except Exception as e:
                    results.append({
                        'index': i,
                        'filename': file.filename,
                        'success': False,
                        'error': str(e)
                    })
            else:
                results.append({
                    'index': i,
                    'success': False,
                    'error': 'No filename'
                })
        
        return jsonify({'results': results})
        
    except Exception as e:
        logger.error(f"ViT batch classification error: {e}")
        return jsonify({'error': str(e)}), 500

@ml_bp.route('/classify/multimodal', methods=['POST'])
def multimodal_classify():
    """Classify using both BERT and ViT (multimodal)"""
    try:
        from ..services.bert_classification_service import classify_text
        from ..services.vit_classification_service import classify_image
        
        results = {}
        
        # Check for text
        text = None
        if request.is_json:
            data = request.get_json()
            text = data.get('text', '')
        else:
            text = request.form.get('text', '')
        
        if text and text.strip():
            results['text_classification'] = classify_text(text)
        
        # Check for image
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                image_bytes = file.read()
                if image_bytes:
                    results['image_classification'] = classify_image(image_bytes)
        
        if not results:
            return jsonify({'error': 'No text or image provided'}), 400
        
        # Combine results if both are available
        if 'text_classification' in results and 'image_classification' in results:
            text_result = results['text_classification']
            image_result = results['image_classification']
            
            if text_result.get('success') and image_result.get('success'):
                # Simple fusion: average confidence scores
                text_conf = text_result['top_prediction']['confidence']
                image_conf = image_result['top_prediction']['confidence']
                
                results['fusion'] = {
                    'method': 'confidence_averaging',
                    'text_weight': 0.5,
                    'image_weight': 0.5,
                    'combined_confidence': (text_conf + image_conf) / 2,
                    'agreement': text_result['top_prediction']['category'] == image_result['top_prediction']['category']
                }
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Multimodal classification error: {e}")
        return jsonify({'error': str(e)}), 500
