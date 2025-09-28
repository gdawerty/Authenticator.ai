"""
Clone Search API Routes - FC-5 Implementation
Unified clone search API with fused top-k results
"""

from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from backend.services.fingerprint_service import FingerprintService
from backend.services.parsing_service import ParsingService

clone_search_bp = Blueprint("clone_search", __name__, url_prefix="/api/clone")
api = Api(clone_search_bp,
         title="Clone Search API",
         version="1.0",
         description="FC-5: Unified clone detection and search API",
         doc="/")

# Initialize services
fingerprint_service = FingerprintService()
parsing_service = ParsingService()

# API Models
clone_search_request = api.model('CloneSearchRequest', {
    'query_type': fields.String(required=True,
                               description='Type of search query',
                               enum=['text', 'image', 'document', 'all'],
                               example='all'),
    'similarity_threshold': fields.Float(description='Similarity threshold (0-1)', default=0.8),
    'max_results': fields.Integer(description='Maximum results to return', default=10)
})

clone_match = api.model('CloneMatch', {
    'doc_id': fields.String(description='Document identifier'),
    'filename': fields.String(description='Original filename'),
    'modality': fields.String(description='Detection modality', enum=['text', 'image', 'template']),
    'method': fields.String(description='Detection method', enum=['simhash', 'phash', 'dhash', 'template_hash']),
    'distance': fields.Float(description='Distance score (0=exact match)'),
    'similarity_score': fields.Float(description='Similarity score (1=exact match)'),
    'match_details': fields.Raw(description='Additional match information')
})

clone_search_response = api.model('CloneSearchResponse', {
    'query_id': fields.String(description='Unique query identifier'),
    'query_timestamp': fields.DateTime(description='Query timestamp'),
    'total_matches': fields.Integer(description='Total matches found'),
    'execution_time_ms': fields.Float(description='Query execution time in milliseconds'),
    'matches': fields.List(fields.Nested(clone_match), description='Fused top-k clone matches'),
    'query_fingerprints': fields.Raw(description='Generated fingerprints for the query'),
    'search_statistics': fields.Raw(description='Search performance metrics')
})

# Parser for file uploads
upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                          type=FileStorage, required=True,
                          help='Document file to search for clones')
upload_parser.add_argument('query_type', location='form',
                          type=str, required=False,
                          choices=['text', 'image', 'document', 'all'],
                          help='Type of clone search to perform',
                          default='all')
upload_parser.add_argument('similarity_threshold', location='form',
                          type=float, required=False,
                          help='Similarity threshold (0-1)',
                          default=0.8)
upload_parser.add_argument('max_results', location='form',
                          type=int, required=False,
                          help='Maximum results to return',
                          default=10)

@api.route('/search')
@api.expect(upload_parser)
class CloneSearch(Resource):
    """FC-5: Unified clone search with fused top-k results"""

    @api.doc('clone_search')
    @api.response(200, 'Success', clone_search_response)
    @api.response(400, 'Invalid file or parameters')
    @api.response(413, 'File too large')
    def post(self):
        """Search for clones of uploaded document across all modalities"""
        start_time = datetime.now()

        try:
            args = upload_parser.parse_args()
            file = args['file']
            query_type = args.get('query_type', 'all')
            similarity_threshold = args.get('similarity_threshold', 0.8)
            max_results = args.get('max_results', 10)

            if not file or file.filename == '':
                return {'error': 'No file provided'}, 400

            # Check file size (16MB limit)
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)

            if file_size > 16 * 1024 * 1024:  # 16MB
                return {'error': 'File size exceeds 16MB limit'}, 413

            # Generate unique identifiers
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            original_filename = secure_filename(file.filename)
            query_id = f"clone_search_{timestamp}_{unique_id}"
            temp_filename = f"temp_{query_id}.{original_filename.rsplit('.', 1)[1].lower()}"

            # Save file temporarily
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tmp_uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, temp_filename)
            file.save(file_path)

            # Determine file type
            file_ext = original_filename.rsplit('.', 1)[1].lower()
            file_type = file_ext

            # Extract text content if needed
            text_content = None
            if query_type in ['text', 'document', 'all']:
                try:
                    # Handle plain text files directly
                    if file_ext in ['txt', 'md', 'csv']:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            text_content = f.read()
                    else:
                        # Use parsing service for other file types
                        mime_type_map = {
                            'pdf': 'application/pdf',
                            'png': 'image/png',
                            'jpg': 'image/jpeg',
                            'jpeg': 'image/jpeg',
                            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                        }
                        mime_type = mime_type_map.get(file_ext, 'application/octet-stream')

                        parse_result = parsing_service.parse_file(file_path, original_filename, mime_type)
                        text_content = parse_result.get('raw_text', '')
                except Exception as e:
                    print(f"Text extraction failed: {e}")

            # Generate query fingerprints (without storing in DB)
            query_fingerprints = {}
            all_matches = []

            # Text fingerprinting and search
            if (query_type in ['text', 'all']) and text_content and len(text_content.strip()) > 10:
                try:
                    text_fp = self._generate_temp_text_fingerprint(text_content, query_id)
                    query_fingerprints['text'] = text_fp

                    text_matches = self._search_text_clones(text_fp, similarity_threshold, max_results)
                    for match in text_matches:
                        match['modality'] = 'text'
                        all_matches.append(match)
                except Exception as e:
                    print(f"Text clone search failed: {e}")

            # Image fingerprinting and search
            if (query_type in ['image', 'all']) and file_type.lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                try:
                    with open(file_path, 'rb') as f:
                        image_bytes = f.read()

                    image_fp = self._generate_temp_image_fingerprint(image_bytes, query_id)
                    query_fingerprints['image'] = image_fp

                    image_matches = self._search_image_clones(image_fp, similarity_threshold, max_results)
                    for match in image_matches:
                        match['modality'] = 'image'
                        all_matches.append(match)
                except Exception as e:
                    print(f"Image clone search failed: {e}")

            # Document template fingerprinting and search
            if (query_type in ['document', 'all']) and text_content:
                try:
                    doc_fp = self._generate_temp_document_fingerprint(text_content, query_id, file_type)
                    query_fingerprints['document'] = doc_fp

                    doc_matches = self._search_document_clones(doc_fp, similarity_threshold, max_results)
                    for match in doc_matches:
                        match['modality'] = 'template'
                        all_matches.append(match)
                except Exception as e:
                    print(f"Document clone search failed: {e}")

            # Fuse and rank results
            fused_matches = self._fuse_clone_results(all_matches, max_results)

            # Calculate execution time
            end_time = datetime.now()
            execution_time_ms = (end_time - start_time).total_seconds() * 1000

            # Build response
            result = {
                'query_id': query_id,
                'query_timestamp': start_time.isoformat(),
                'total_matches': len(fused_matches),
                'execution_time_ms': execution_time_ms,
                'matches': fused_matches,
                'query_fingerprints': query_fingerprints,
                'search_statistics': {
                    'query_type': query_type,
                    'similarity_threshold': similarity_threshold,
                    'file_type': file_type,
                    'file_size_bytes': file_size,
                    'text_extracted': bool(text_content),
                    'modalities_searched': list(query_fingerprints.keys())
                }
            }

            # Clean up temp file
            try:
                os.remove(file_path)
            except:
                pass

            return result, 200

        except Exception as e:
            return {'error': f'Clone search failed: {str(e)}'}, 500

    def _generate_temp_text_fingerprint(self, text: str, query_id: str) -> dict:
        """Generate text fingerprint without storing in DB"""
        cleaned_text = fingerprint_service._clean_text(text)
        shingles = fingerprint_service._generate_shingles(cleaned_text, n=3)
        simhash = fingerprint_service._generate_simhash(shingles)
        embedding_hash = fingerprint_service._generate_embedding_hash(cleaned_text)

        return {
            'query_id': query_id,
            'simhash': simhash,
            'shingles': shingles[:50],  # First 50 for debugging
            'embedding_hash': embedding_hash,
            'text_length': len(text)
        }

    def _generate_temp_image_fingerprint(self, image_bytes: bytes, query_id: str) -> dict:
        """Generate image fingerprint without storing in DB"""
        import imagehash
        from PIL import Image
        from io import BytesIO

        image = Image.open(BytesIO(image_bytes))

        return {
            'query_id': query_id,
            'phash': str(imagehash.phash(image)),
            'dhash': str(imagehash.dhash(image)),
            'ahash': str(imagehash.average_hash(image)),
            'whash': str(imagehash.whash(image)),
            'image_size': f"{image.width}x{image.height}"
        }

    def _generate_temp_document_fingerprint(self, text: str, query_id: str, file_type: str) -> dict:
        """Generate document template fingerprint without storing in DB"""
        template_hash = fingerprint_service._generate_template_hash(text)
        structure_hash = fingerprint_service._generate_structure_hash(text)
        layout_features = fingerprint_service._extract_layout_features(text)

        return {
            'query_id': query_id,
            'template_hash': template_hash,
            'structure_hash': structure_hash,
            'layout_features': layout_features,
            'file_type': file_type
        }

    def _search_text_clones(self, query_fp: dict, threshold: float, max_results: int) -> list:
        """Search for text clones using SimHash and embedding similarity"""
        import sqlite3

        matches = []
        conn = sqlite3.connect(fingerprint_service.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT file_id, filename, simhash, embedding_hash FROM text_fingerprints')
        results = cursor.fetchall()

        query_simhash = query_fp['simhash']
        query_embedding = query_fp['embedding_hash']

        for row in results:
            file_id, filename, stored_simhash, stored_embedding = row

            # Calculate SimHash distance
            if stored_simhash and query_simhash:
                hamming_distance = bin(int(query_simhash, 2) ^ int(stored_simhash, 2)).count('1')
                similarity_score = 1.0 - (hamming_distance / 64.0)

                if similarity_score >= threshold:
                    matches.append({
                        'doc_id': file_id,
                        'filename': filename,
                        'method': 'simhash',
                        'distance': hamming_distance,
                        'similarity_score': similarity_score,
                        'match_details': {
                            'hamming_distance': hamming_distance,
                            'simhash_query': query_simhash[:16],
                            'simhash_stored': stored_simhash[:16] if stored_simhash else None
                        }
                    })

            # Check embedding exact match
            if stored_embedding == query_embedding:
                matches.append({
                    'doc_id': file_id,
                    'filename': filename,
                    'method': 'embedding_exact',
                    'distance': 0,
                    'similarity_score': 1.0,
                    'match_details': {
                        'embedding_hash': query_embedding
                    }
                })

        conn.close()

        # Sort by similarity score and limit results
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        return matches[:max_results]

    def _search_image_clones(self, query_fp: dict, threshold: float, max_results: int) -> list:
        """Search for image clones using perceptual hashes"""
        import sqlite3

        matches = []
        conn = sqlite3.connect(fingerprint_service.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT file_id, filename, phash, dhash, ahash, whash FROM image_fingerprints')
        results = cursor.fetchall()

        for row in results:
            file_id, filename, stored_phash, stored_dhash, stored_ahash, stored_whash = row

            # Calculate hash distances
            hash_distances = {}
            hash_similarities = {}

            for hash_type, query_hash, stored_hash in [
                ('phash', query_fp.get('phash'), stored_phash),
                ('dhash', query_fp.get('dhash'), stored_dhash),
                ('ahash', query_fp.get('ahash'), stored_ahash),
                ('whash', query_fp.get('whash'), stored_whash)
            ]:
                if query_hash and stored_hash:
                    try:
                        distance = bin(int(query_hash, 16) ^ int(stored_hash, 16)).count('1')
                        similarity = 1.0 - (distance / 64.0)
                        hash_distances[hash_type] = distance
                        hash_similarities[hash_type] = similarity
                    except:
                        continue

            if hash_similarities:
                # Use best similarity score
                best_similarity = max(hash_similarities.values())
                best_method = max(hash_similarities, key=hash_similarities.get)
                best_distance = hash_distances[best_method]

                if best_similarity >= threshold:
                    matches.append({
                        'doc_id': file_id,
                        'filename': filename,
                        'method': best_method,
                        'distance': best_distance,
                        'similarity_score': best_similarity,
                        'match_details': {
                            'all_similarities': hash_similarities,
                            'best_hash_type': best_method
                        }
                    })

        conn.close()

        # Sort by similarity score and limit results
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        return matches[:max_results]

    def _search_document_clones(self, query_fp: dict, threshold: float, max_results: int) -> list:
        """Search for document template clones"""
        import sqlite3

        matches = []
        conn = sqlite3.connect(fingerprint_service.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT file_id, filename, template_hash, structure_hash FROM document_fingerprints')
        results = cursor.fetchall()

        query_template = query_fp['template_hash']
        query_structure = query_fp['structure_hash']

        for row in results:
            file_id, filename, stored_template, stored_structure = row

            # Check exact template match
            if stored_template == query_template:
                matches.append({
                    'doc_id': file_id,
                    'filename': filename,
                    'method': 'template_exact',
                    'distance': 0,
                    'similarity_score': 1.0,
                    'match_details': {
                        'template_hash': query_template
                    }
                })

            # Check structure match
            elif stored_structure == query_structure and threshold <= 0.85:
                matches.append({
                    'doc_id': file_id,
                    'filename': filename,
                    'method': 'structure_match',
                    'distance': 0.15,
                    'similarity_score': 0.85,
                    'match_details': {
                        'structure_hash': query_structure
                    }
                })

        conn.close()

        # Sort by similarity score and limit results
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        return matches[:max_results]

    def _fuse_clone_results(self, all_matches: list, max_results: int) -> list:
        """Fuse and rank clone results from multiple modalities"""
        # Group by document ID to combine modality results
        doc_groups = {}

        for match in all_matches:
            doc_id = match['doc_id']
            if doc_id not in doc_groups:
                doc_groups[doc_id] = []
            doc_groups[doc_id].append(match)

        # Create fused results
        fused_matches = []

        for doc_id, matches in doc_groups.items():
            # Use best similarity score across modalities
            best_match = max(matches, key=lambda x: x['similarity_score'])

            # Create fused result
            fused_match = {
                'doc_id': doc_id,
                'filename': best_match['filename'],
                'modality': best_match['modality'],
                'method': best_match['method'],
                'distance': best_match['distance'],
                'similarity_score': best_match['similarity_score'],
                'match_details': {
                    'primary_match': best_match['match_details'],
                    'all_modalities': [m['modality'] for m in matches],
                    'all_methods': [m['method'] for m in matches],
                    'modality_count': len(matches)
                }
            }

            fused_matches.append(fused_match)

        # Sort by similarity score and limit results
        fused_matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        return fused_matches[:max_results]

@api.route('/statistics')
class CloneSearchStatistics(Resource):
    """Clone search performance statistics"""

    @api.doc('clone_search_statistics')
    @api.response(200, 'Statistics retrieved successfully')
    def get(self):
        """Get clone search performance and database statistics"""
        try:
            stats = fingerprint_service.get_clone_statistics()

            # Add search-specific metrics
            search_stats = {
                'database_statistics': stats,
                'search_performance': {
                    'average_query_time_ms': 85.0,  # Would track actual metrics
                    'queries_last_24h': 0,  # Would track from logs
                    'cache_hit_rate': 0.0,
                    'index_coverage': {
                        'text_index_size': stats['total_text_fingerprints'],
                        'image_index_size': stats['total_image_fingerprints'],
                        'template_index_size': stats['total_document_fingerprints']
                    }
                },
                'last_updated': datetime.now().isoformat()
            }

            return search_stats, 200

        except Exception as e:
            return {'error': f'Failed to retrieve clone search statistics: {str(e)}'}, 500