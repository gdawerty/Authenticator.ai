"""
Stage 3 Clone Detection API Routes
Enhanced SimHash & MinHash implementation for the authenticity pipeline
"""

from flask import request, jsonify
from flask_restx import Resource, fields, Namespace
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import os
import uuid
import json
import sqlite3
from datetime import datetime

from ..services.enhanced_clone_detection_service import enhanced_clone_detection_service
from ..services.parsing_service import parsing_service

# Create namespace
api = Namespace('stage3_clone_detection', description='Stage 3: Enhanced Clone Detection using SimHash & MinHash')

# Request parsers
upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True, help='Document to analyze')
upload_parser.add_argument('similarity_threshold', type=float, default=0.85, help='Similarity threshold (0-1)')
upload_parser.add_argument('document_type', type=str, required=False, help='Optional document type hint')
upload_parser.add_argument('auto_train', type=str, default='prompt', help='Training mode: "true", "false", or "prompt"')

# Response models
similarity_match_model = api.model('SimilarityMatch', {
    'file_id': fields.String(description='Matched document ID'),
    'filename': fields.String(description='Matched document filename'),
    'similarity_score': fields.Float(description='Similarity score (0-1)'),
    'match_method': fields.String(description='Detection method', enum=['simhash', 'minhash', 'combined']),
    'hamming_distance': fields.Integer(description='SimHash Hamming distance'),
    'jaccard_similarity': fields.Float(description='MinHash Jaccard similarity'),
    'match_details': fields.Raw(description='Additional match metadata')
})

fingerprint_data_model = api.model('FingerprintData', {
    'simhash': fields.String(description='64-bit SimHash value'),
    'minhash_signature_length': fields.Integer(description='MinHash signature length'),
    'shingles_count': fields.Integer(description='Number of shingles generated'),
    'text_length': fields.Integer(description='Original text length')
})

metadata_model = api.model('ProcessingMetadata', {
    'document_type': fields.String(description='Document type classification'),
    'processing_time_ms': fields.Float(description='Processing time in milliseconds'),
    'similarity_threshold': fields.Float(description='Similarity threshold used'),
    'timestamp': fields.String(description='Processing timestamp')
})

stage3_response_model = api.model('Stage3CloneDetectionResponse', {
    'file_id': fields.String(description='Unique file identifier'),
    'filename': fields.String(description='Original filename'),
    'similarity_score': fields.Float(description='Maximum similarity score found (0-1)'),
    'duplicates_found': fields.Integer(description='Number of near-duplicates found'),
    'similarity_matches': fields.List(fields.Nested(similarity_match_model), description='Similar documents found'),
    'fingerprint_data': fields.Nested(fingerprint_data_model, description='Generated fingerprint metadata'),
    'metadata': fields.Nested(metadata_model, description='Processing metadata'),
    'pipeline_stage': fields.String(description='Pipeline stage identifier', default='stage_3_clone_detection')
})

statistics_model = api.model('CloneDetectionStatistics', {
    'total_fingerprints': fields.Integer(description='Total fingerprints in database'),
    'total_similarity_matches': fields.Integer(description='Total similarity matches cached'),
    'average_similarity_score': fields.Float(description='Average similarity score'),
    'method_distribution': fields.Raw(description='Distribution of detection methods'),
    'simhash_bits': fields.Integer(description='SimHash bit length'),
    'minhash_permutations': fields.Integer(description='MinHash permutation count'),
    'similarity_threshold': fields.Float(description='Current similarity threshold')
})


@api.route('/analyze')
@api.expect(upload_parser)
class Stage3CloneDetection(Resource):
    """Stage 3: Enhanced clone detection using SimHash & MinHash with training options"""

    @api.doc('stage3_clone_detection')
    @api.response(200, 'Success', stage3_response_model)
    @api.response(400, 'Invalid file or parameters')
    @api.response(413, 'File too large')
    @api.response(500, 'Processing error')
    def post(self):
        """
        Analyze document for clones using enhanced SimHash & MinHash detection
        
        Pipeline Stage 3 Implementation:
        1. Generate SimHash for approximate similarity in bit space
        2. Generate MinHash for set-similarity detection (textual overlap)
        3. Compare against local hash index of known documents
        4. OPTIONALLY TRAIN based on user preference or auto_train parameter
        5. Return similarity score (0-1) and matched document metadata
        
        Training Modes:
        - auto_train="true": Automatically train on the document
        - auto_train="false": Only analyze, don't train
        - auto_train="prompt": Return analysis with training recommendation
        """
        try:
            # Parse request
            args = upload_parser.parse_args()
            file = args['file']
            similarity_threshold = args.get('similarity_threshold', 0.85)
            document_type = args.get('document_type')
            auto_train_mode = args.get('auto_train', 'prompt').lower()
            
            if not file or file.filename == '':
                return {'error': 'No file provided'}, 400
            
            # Update service threshold if provided
            if similarity_threshold != enhanced_clone_detection_service.similarity_threshold:
                enhanced_clone_detection_service.update_similarity_threshold(similarity_threshold)
            
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            original_filename = secure_filename(file.filename)
            
            # Save file temporarily
            upload_dir = "tmp_uploads"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, f"{file_id}_{original_filename}")
            file.save(file_path)
            
            try:
                # Extract text content
                text_content = parsing_service.extract_text_from_file(file_path)
                
                if not text_content or len(text_content.strip()) < 10:
                    return {
                        'error': 'Unable to extract sufficient text content from file',
                        'file_id': file_id,
                        'filename': original_filename
                    }, 400
                
                # Determine training behavior based on auto_train parameter
                if auto_train_mode == "prompt":
                    # First, analyze without training to get results
                    analysis_result = enhanced_clone_detection_service.process_document(
                        text=text_content,
                        file_id=file_id,
                        filename=original_filename,
                        document_type=document_type,
                        auto_train=False  # Don't train yet
                    )
                    
                    # Generate training recommendation
                    training_recommendation = self._generate_training_recommendation(
                        analysis_result, text_content
                    )
                    
                    # Return analysis with training option
                    result = analysis_result.copy()
                    result['training_recommendation'] = training_recommendation
                    result['pipeline_stage'] = 'stage_3_clone_detection_with_training_prompt'
                    
                elif auto_train_mode == "true":
                    # Process with automatic training
                    result = enhanced_clone_detection_service.process_document(
                        text=text_content,
                        file_id=file_id,
                        filename=original_filename,
                        document_type=document_type,
                        auto_train=True
                    )
                    result['pipeline_stage'] = 'stage_3_clone_detection_with_training'
                    
                elif auto_train_mode == "false":
                    # Process without training
                    result = enhanced_clone_detection_service.process_document(
                        text=text_content,
                        file_id=file_id,
                        filename=original_filename,
                        document_type=document_type,
                        auto_train=False
                    )
                    result['pipeline_stage'] = 'stage_3_clone_detection_no_training'
                    
                else:
                    return {'error': 'Invalid auto_train value. Use "true", "false", or "prompt"'}, 400
                
                return result, 200
                
            finally:
                # Clean up temporary file
                try:
                    os.remove(file_path)
                except OSError:
                    pass
                    
        except ValueError as e:
            return {'error': f'Invalid parameter: {str(e)}'}, 400
        except Exception as e:
            return {'error': f'Clone detection failed: {str(e)}'}, 500
    
    def _generate_training_recommendation(self, analysis_result: dict, text_content: str) -> dict:
        """Generate training recommendation based on analysis results"""
        recommendation = {
            'should_train': False,
            'confidence': 'low',
            'reasons': [],
            'benefits': [],
            'concerns': []
        }
        
        similarity_score = analysis_result.get('similarity_score', 0.0)
        matches = analysis_result.get('similarity_matches', [])
        text_length = len(text_content)
        
        # Analyze if training would be beneficial
        if similarity_score < 0.95:  # Not a near-duplicate
            recommendation['should_train'] = True
            recommendation['reasons'].append('Document is unique enough to add value to training set')
            
            if text_length > 200:
                recommendation['confidence'] = 'high'
                recommendation['benefits'].append('Good content length for meaningful fingerprints')
            elif text_length > 50:
                recommendation['confidence'] = 'medium'
                recommendation['benefits'].append('Adequate content for training')
            else:
                recommendation['confidence'] = 'low'
                recommendation['concerns'].append('Document might be too short for effective training')
            
            if len(matches) == 0:
                recommendation['benefits'].append('No similar documents found - adds new knowledge')
            elif len(matches) > 0 and similarity_score < 0.85:
                recommendation['benefits'].append('Moderate similarity - helps refine detection boundaries')
            
        else:
            recommendation['should_train'] = False
            recommendation['reasons'].append(f'Document too similar to existing ({similarity_score:.1%})')
            recommendation['concerns'].append('Training on near-duplicates can reduce detection accuracy')
        
        # Additional analysis
        if analysis_result.get('duplicates_found', 0) > 0:
            recommendation['concerns'].append('High similarity detected - consider if this adds unique value')
        
        return recommendation


@api.route('/batch_analyze')
class BatchCloneDetection(Resource):
    """Batch clone detection for multiple documents"""

    @api.doc('batch_clone_detection')
    def post(self):
        """
        Analyze multiple documents for cross-clones and similarities
        Useful for detecting clone networks and document families
        """
        try:
            # Get list of file IDs or text content from request
            data = request.get_json()
            
            if not data or 'documents' not in data:
                return {'error': 'No documents provided'}, 400
            
            documents = data['documents']
            similarity_threshold = data.get('similarity_threshold', 0.85)
            
            # Update service threshold
            enhanced_clone_detection_service.update_similarity_threshold(similarity_threshold)
            
            batch_results = []
            document_pairs = []
            
            # Process each document
            for i, doc in enumerate(documents):
                if 'text' not in doc:
                    continue
                    
                file_id = doc.get('file_id', f'batch_{i}_{uuid.uuid4()}')
                filename = doc.get('filename', f'document_{i}.txt')
                document_type = doc.get('document_type')
                
                result = enhanced_clone_detection_service.process_document(
                    text=doc['text'],
                    file_id=file_id,
                    filename=filename,
                    document_type=document_type
                )
                
                batch_results.append(result)
            
            # Analyze cross-document similarities
            for i in range(len(batch_results)):
                for j in range(i + 1, len(batch_results)):
                    doc1 = batch_results[i]
                    doc2 = batch_results[j]
                    
                    # Check if they matched each other
                    doc1_matches = [m['file_id'] for m in doc1['similarity_matches']]
                    doc2_matches = [m['file_id'] for m in doc2['similarity_matches']]
                    
                    if doc1['file_id'] in doc2_matches or doc2['file_id'] in doc1_matches:
                        document_pairs.append({
                            'doc1_id': doc1['file_id'],
                            'doc1_filename': doc1['filename'],
                            'doc2_id': doc2['file_id'], 
                            'doc2_filename': doc2['filename'],
                            'cross_similarity': max(
                                [m['similarity_score'] for m in doc1['similarity_matches'] if m['file_id'] == doc2['file_id']] + [0],
                                [m['similarity_score'] for m in doc2['similarity_matches'] if m['file_id'] == doc1['file_id']] + [0]
                            )
                        })
            
            return {
                'batch_id': str(uuid.uuid4()),
                'total_documents': len(documents),
                'processed_documents': len(batch_results),
                'document_results': batch_results,
                'cross_document_pairs': document_pairs,
                'similarity_threshold': similarity_threshold,
                'timestamp': datetime.now().isoformat()
            }, 200
            
        except Exception as e:
            return {'error': f'Batch clone detection failed: {str(e)}'}, 500


@api.route('/statistics')
class CloneDetectionStatistics(Resource):
    """Get clone detection system statistics"""

    @api.doc('clone_detection_stats')
    @api.response(200, 'Success', statistics_model)
    def get(self):
        """Get comprehensive statistics about the clone detection system"""
        try:
            stats = enhanced_clone_detection_service.get_statistics()
            return stats, 200
        except Exception as e:
            return {'error': f'Failed to get statistics: {str(e)}'}, 500


@api.route('/threshold')
class SimilarityThreshold(Resource):
    """Manage similarity threshold settings"""

    @api.doc('get_threshold')
    def get(self):
        """Get current similarity threshold"""
        return {
            'similarity_threshold': enhanced_clone_detection_service.similarity_threshold,
            'description': 'Minimum similarity score (0-1) to consider documents as similar'
        }, 200

    @api.doc('update_threshold')
    def put(self):
        """Update similarity threshold"""
        try:
            data = request.get_json()
            if not data or 'threshold' not in data:
                return {'error': 'Threshold value required'}, 400
            
            new_threshold = float(data['threshold'])
            enhanced_clone_detection_service.update_similarity_threshold(new_threshold)
            
            return {
                'message': 'Threshold updated successfully',
                'old_threshold': enhanced_clone_detection_service.similarity_threshold,
                'new_threshold': new_threshold
            }, 200
            
        except ValueError as e:
            return {'error': f'Invalid threshold value: {str(e)}'}, 400
        except Exception as e:
            return {'error': f'Failed to update threshold: {str(e)}'}, 500


@api.route('/search/<file_id>')
class SearchSimilarDocuments(Resource):
    """Search for documents similar to a specific file ID"""

    @api.doc('search_similar')
    def get(self, file_id):
        """Find documents similar to the specified file ID"""
        try:
            # Get the fingerprints for this file
            conn = sqlite3.connect(enhanced_clone_detection_service.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT simhash, minhash_signature, filename 
                FROM enhanced_fingerprints 
                WHERE file_id = ?
            ''', (file_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {'error': f'File ID {file_id} not found'}, 404
            
            simhash, minhash_sig_str, filename = result
            minhash_signature = json.loads(minhash_sig_str) if minhash_sig_str else []
            
            # Search for similar documents
            fingerprints = {
                'simhash': simhash,
                'minhash_signature': minhash_signature
            }
            
            similar_docs = enhanced_clone_detection_service._search_similar_documents(fingerprints)
            
            return {
                'query_file_id': file_id,
                'query_filename': filename,
                'total_matches': len(similar_docs),
                'similar_documents': similar_docs,
                'similarity_threshold': enhanced_clone_detection_service.similarity_threshold,
                'timestamp': datetime.now().isoformat()
            }, 200
            
        except Exception as e:
            return {'error': f'Search failed: {str(e)}'}, 500


@api.route('/training/quality')
class TrainingQualityMetrics(Resource):
    """Get training data quality metrics"""

    @api.doc('training_quality')
    def get(self):
        """Get comprehensive training data quality metrics"""
        try:
            quality_metrics = enhanced_clone_detection_service.get_training_quality_metrics()
            return quality_metrics, 200
        except Exception as e:
            return {'error': f'Failed to get quality metrics: {str(e)}'}, 500


@api.route('/training/remove/<file_id>')
class RemoveFromTraining(Resource):
    """Remove a document from the training set"""

    @api.doc('remove_training')
    def delete(self, file_id):
        """Remove a specific document from the training set"""
        try:
            result = enhanced_clone_detection_service.remove_document_from_training(file_id)
            
            if result['success']:
                return result, 200
            else:
                return result, 400
                
        except Exception as e:
            return {'error': f'Failed to remove document: {str(e)}'}, 500


@api.route('/training/analyze_without_storing')
@api.expect(upload_parser)
class AnalyzeWithoutTraining(Resource):
    """Analyze document without adding it to training set"""

    @api.doc('analyze_no_train')
    def post(self):
        """
        Analyze document for clones WITHOUT adding it to the training set
        Useful for testing or analyzing sensitive documents
        """
        try:
            # Parse request
            args = upload_parser.parse_args()
            file = args['file']
            similarity_threshold = args.get('similarity_threshold', 0.85)
            document_type = args.get('document_type')
            
            if not file or file.filename == '':
                return {'error': 'No file provided'}, 400
            
            # Update service threshold if provided
            if similarity_threshold != enhanced_clone_detection_service.similarity_threshold:
                enhanced_clone_detection_service.update_similarity_threshold(similarity_threshold)
            
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            original_filename = secure_filename(file.filename)
            
            # Save file temporarily
            upload_dir = "tmp_uploads"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, f"{file_id}_{original_filename}")
            file.save(file_path)
            
            try:
                # Extract text content
                text_content = parsing_service.extract_text_from_file(file_path)
                
                if not text_content or len(text_content.strip()) < 10:
                    return {
                        'error': 'Unable to extract sufficient text content from file',
                        'file_id': file_id,
                        'filename': original_filename
                    }, 400
                
                # Process document WITHOUT auto-training
                result = enhanced_clone_detection_service.process_document(
                    text=text_content,
                    file_id=file_id,
                    filename=original_filename,
                    document_type=document_type,
                    auto_train=False  # Disable automatic training
                )
                
                # Add pipeline stage identifier
                result['pipeline_stage'] = 'stage_3_clone_detection_no_training'
                
                return result, 200
                
            finally:
                # Clean up temporary file
                try:
                    os.remove(file_path)
                except OSError:
                    pass
                    
        except ValueError as e:
            return {'error': f'Invalid parameter: {str(e)}'}, 400
        except Exception as e:
            return {'error': f'Clone detection failed: {str(e)}'}, 500


@api.route('/training/confirm')
class ConfirmTraining(Resource):
    """Confirm training on a previously analyzed document"""

    @api.doc('confirm_training')
    def post(self):
        """
        Train the system on a document that was previously analyzed with training_recommendation
        """
        try:
            data = request.get_json()
            
            if not data:
                return {'error': 'JSON data required'}, 400
                
            # Required fields
            required_fields = ['file_id', 'text', 'filename']
            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400
            
            file_id = data['file_id']
            text = data['text']
            filename = data['filename']
            document_type = data.get('document_type', 'user_confirmed')
            user_decision = data.get('train', True)
            
            if user_decision:
                # User confirmed training - process with training enabled
                result = enhanced_clone_detection_service.process_document(
                    text=text,
                    file_id=file_id,
                    filename=filename,
                    document_type=document_type,
                    auto_train=True
                )
                
                return {
                    'message': 'Document successfully trained',
                    'training_status': result['training_status'],
                    'file_id': file_id,
                    'timestamp': datetime.now().isoformat()
                }, 200
            else:
                # User declined training
                return {
                    'message': 'Training declined by user',
                    'file_id': file_id,
                    'training_status': {
                        'trained': False,
                        'reason': 'User declined training',
                        'user_declined': True
                    },
                    'timestamp': datetime.now().isoformat()
                }, 200
                
        except Exception as e:
            return {'error': f'Training confirmation failed: {str(e)}'}, 500


@api.route('/training/manual_add')
class ManualTraining(Resource):
    """Manually add text to training set"""

    @api.doc('manual_training')
    def post(self):
        """Manually add text content to the training set"""
        try:
            data = request.get_json()
            
            if not data or 'text' not in data:
                return {'error': 'Text content required'}, 400
                
            text = data['text']
            file_id = data.get('file_id', f'manual_{uuid.uuid4()}')
            filename = data.get('filename', 'manual_training.txt')
            document_type = data.get('document_type', 'manual')
            
            # Process with training enabled
            result = enhanced_clone_detection_service.process_document(
                text=text,
                file_id=file_id,
                filename=filename,
                document_type=document_type,
                auto_train=True
            )
            
            return {
                'message': 'Document processed and added to training set',
                'training_status': result['training_status'],
                'file_id': result['file_id'],
                'similarity_score': result['similarity_score']
            }, 200
            
        except Exception as e:
            return {'error': f'Manual training failed: {str(e)}'}, 500
