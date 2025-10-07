"""
AI Clone Detection API Routes
Provides endpoints for advanced image and document clone detection
"""

from flask import Blueprint, request, jsonify
import os
import tempfile
from werkzeug.utils import secure_filename
from services.ai_clone_detection_service import AICloneDetectionService
from services.parsing_service import ParsingService

ai_clone_routes = Blueprint('ai_clone_detection', __name__)
ai_clone_service = AICloneDetectionService()
parsing_service = ParsingService()


@ai_clone_routes.route('/ai-clone-detection/compare', methods=['POST'])
def compare_files_ai():
    """
    AI clone-detection assistant endpoint that identifies whether two files are duplicates,
    near-duplicates, or partial clones using advanced embedding techniques.
    
    Expected form data:
    - file1: First file (image or document)
    - file2: Second file (image or document)  
    - file1_type: Type of first file ('image' or 'document')
    - file2_type: Type of second file ('image' or 'document')
    
    Returns structured JSON result with:
    - global_similarity (0–1)
    - mean_local_similarity (0–1) 
    - partial_clone_regions (if any, [x,y,w,h] for images or sentence indices for docs)
    - clone_verdict ("clone", "partial_clone", "different")
    - reasoning: Detailed explanation
    """
    try:
        # Validate request
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({
                "error": "Both file1 and file2 are required",
                "status": "error"
            }), 400
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        file1_type = request.form.get('file1_type', 'document').lower()
        file2_type = request.form.get('file2_type', 'document').lower()
        
        if file1.filename == '' or file2.filename == '':
            return jsonify({
                "error": "Both files must have filenames",
                "status": "error"
            }), 400
        
        # Validate file types
        supported_types = ['image', 'document']
        if file1_type not in supported_types or file2_type not in supported_types:
            return jsonify({
                "error": f"Supported file types: {supported_types}",
                "status": "error"
            }), 400
        
        # Save files temporarily
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save first file
            file1_filename = secure_filename(file1.filename)
            file1_path = os.path.join(temp_dir, f"file1_{file1_filename}")
            file1.save(file1_path)
            
            # Save second file
            file2_filename = secure_filename(file2.filename)
            file2_path = os.path.join(temp_dir, f"file2_{file2_filename}")
            file2.save(file2_path)
            
            # For document types, extract text if needed
            if file1_type == 'document' and file1_filename.endswith(('.pdf', '.docx', '.doc')):
                try:
                    text1 = parsing_service.extract_text(file1_path)
                    text1_path = os.path.join(temp_dir, "file1_extracted.txt")
                    with open(text1_path, 'w', encoding='utf-8') as f:
                        f.write(text1)
                    file1_path = text1_path
                except Exception as e:
                    print(f"Warning: Could not extract text from file1: {e}")
            
            if file2_type == 'document' and file2_filename.endswith(('.pdf', '.docx', '.doc')):
                try:
                    text2 = parsing_service.extract_text(file2_path)
                    text2_path = os.path.join(temp_dir, "file2_extracted.txt")
                    with open(text2_path, 'w', encoding='utf-8') as f:
                        f.write(text2)
                    file2_path = text2_path
                except Exception as e:
                    print(f"Warning: Could not extract text from file2: {e}")
            
            # Perform AI clone detection analysis
            result = ai_clone_service.compare_files(
                file1_path, file2_path, file1_type, file2_type
            )
            
            # Add API-specific metadata
            result.update({
                "api_endpoint": "/ai-clone-detection/compare",
                "file1_name": file1_filename,
                "file2_name": file2_filename,
                "status": "success"
            })
            
            return jsonify(result), 200
    
    except Exception as e:
        return jsonify({
            "error": f"AI clone detection failed: {str(e)}",
            "status": "error"
        }), 500


@ai_clone_routes.route('/ai-clone-detection/analyze-single', methods=['POST'])
def analyze_single_file():
    """
    Analyze a single file and extract embeddings for future comparisons.
    
    Expected form data:
    - file: File to analyze (image or document)
    - file_type: Type of file ('image' or 'document')
    
    Returns:
    - file_id: Unique identifier for the file
    - embeddings_info: Information about extracted embeddings
    - status: Success/error status
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                "error": "File is required",
                "status": "error"
            }), 400
        
        file = request.files['file']
        file_type = request.form.get('file_type', 'document').lower()
        
        if file.filename == '':
            return jsonify({
                "error": "File must have a filename",
                "status": "error"
            }), 400
        
        if file_type not in ['image', 'document']:
            return jsonify({
                "error": "file_type must be 'image' or 'document'",
                "status": "error"
            }), 400
        
        # Save file temporarily
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            
            # Extract text for documents if needed
            if file_type == 'document' and filename.endswith(('.pdf', '.docx', '.doc')):
                try:
                    text = parsing_service.extract_text(file_path)
                    text_path = os.path.join(temp_dir, "extracted.txt")
                    with open(text_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    file_path = text_path
                except Exception as e:
                    print(f"Warning: Could not extract text: {e}")
            
            # Extract embeddings
            embeddings = ai_clone_service.extract_embeddings(file_path, file_type)
            
            # Generate file ID and store
            file_id = ai_clone_service._generate_file_id(file_path)
            ai_clone_service._store_embeddings(file_id, filename, file_type, embeddings)
            
            # Prepare response
            embeddings_info = {
                "global_embedding_shape": embeddings["global_embedding"].shape,
                "has_local_embeddings": embeddings.get("local_embeddings") is not None,
                "local_embeddings_count": len(embeddings["local_embeddings"]) if embeddings.get("local_embeddings") is not None else 0
            }
            
            if file_type == 'image':
                embeddings_info.update({
                    "image_shape": embeddings.get("image_shape"),
                    "patch_size": embeddings.get("patch_size")
                })
            else:
                embeddings_info.update({
                    "text_length": embeddings.get("text_length"),
                    "sentence_count": embeddings.get("sentence_count", 0)
                })
            
            return jsonify({
                "file_id": file_id,
                "filename": filename,
                "file_type": file_type,
                "embeddings_info": embeddings_info,
                "status": "success"
            }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Single file analysis failed: {str(e)}",
            "status": "error"
        }), 500


@ai_clone_routes.route('/ai-clone-detection/history', methods=['GET'])
def get_analysis_history():
    """
    Get clone detection analysis history.
    
    Query parameters:
    - file_id (optional): Get history for specific file
    - limit (optional): Limit number of results (default: 50)
    """
    try:
        file_id = request.args.get('file_id')
        limit = int(request.args.get('limit', 50))
        
        history = ai_clone_service.get_analysis_history(file_id)
        
        # Limit results
        if limit > 0:
            history = history[:limit]
        
        return jsonify({
            "history": history,
            "count": len(history),
            "status": "success"
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Failed to get analysis history: {str(e)}",
            "status": "error"
        }), 500


@ai_clone_routes.route('/ai-clone-detection/demo', methods=['GET'])
def demo_ai_clone_detection():
    """
    Demo endpoint showing AI clone detection capabilities and example output.
    """
    try:
        from datetime import datetime
        import json
        
        # Example result structure
        example_result = {
            "global_similarity": 0.94,
            "mean_local_similarity": 0.78,
            "partial_clone_regions": [
                {"x": 120, "y": 80, "w": 32, "h": 32, "similarity": 0.73},
                {"x": 200, "y": 150, "w": 32, "h": 32, "similarity": 0.69}
            ],
            "clone_verdict": "partial_clone",
            "reasoning": "Most features are identical (global similarity: 0.940) except local anomalies near coordinates [(120, 80), (200, 150)]. Classified as partial clone.",
            "thresholds": {
                "global_threshold": 0.98,
                "local_threshold": 0.85
            },
            "file1_type": "image",
            "file2_type": "image",
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        capabilities = {
            "supported_file_types": ["image", "document"],
            "embedding_models": ["CLIP", "ViT", "Sentence Transformers"],
            "similarity_metrics": ["cosine_similarity", "normalized_vectors"],
            "detection_capabilities": [
                "Global similarity analysis",
                "Local similarity mapping", 
                "Partial clone region detection",
                "Structured JSON output",
                "Threshold-based classification",
                "Detailed reasoning"
            ],
            "classification_types": ["clone", "partial_clone", "different"],
            "thresholds": {
                "clone_global_threshold": 0.98,
                "clone_local_threshold": 0.85,
                "partial_clone_threshold": 0.80
            }
        }
        
        return jsonify({
            "message": "AI Clone Detection Service - Advanced image and document clone detection",
            "example_result": example_result,
            "capabilities": capabilities,
            "endpoints": {
                "compare": "/ai-clone-detection/compare - Compare two files",
                "analyze": "/ai-clone-detection/analyze-single - Analyze single file",
                "history": "/ai-clone-detection/history - Get analysis history",
                "demo": "/ai-clone-detection/demo - This demo endpoint"
            },
            "status": "ready"
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Demo failed: {str(e)}",
            "status": "error"
        }), 500


@ai_clone_routes.route('/ai-clone-detection/status', methods=['GET'])
def get_service_status():
    """Get AI clone detection service status and model availability."""
    try:
        # Check if models are loaded
        has_clip = ai_clone_service.clip_model is not None
        has_text_model = ai_clone_service.text_model is not None
        
        return jsonify({
            "service_status": "operational",
            "models_loaded": {
                "clip_model": has_clip,
                "text_model": has_text_model
            },
            "database_path": ai_clone_service.db_path,
            "thresholds": {
                "global_similarity_threshold": ai_clone_service.global_similarity_threshold,
                "local_similarity_threshold": ai_clone_service.local_similarity_threshold
            },
            "patch_size": ai_clone_service.patch_size,
            "status": "ready"
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Status check failed: {str(e)}",
            "status": "error"
        }), 500
