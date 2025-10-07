"""
Enhanced Clone Detection Service - Stage 3 Pipeline
Implements SimHash & MinHash for near-duplicate and semantically similar document detection
"""

import hashlib
import numpy as np
import sqlite3
import json
import os
import re
from typing import Dict, List, Tuple, Optional, Any, Set
from datetime import datetime
from collections import defaultdict
import random


class EnhancedCloneDetectionService:
    """
    Stage 3: Clone Detection Layer using SimHash & MinHash
    
    Goal: Detect near-duplicate or semantically similar documents.
    
    How it works:
    - Generate SimHash for each document to capture approximate similarity in bit space
    - Use MinHash (with shingles) for set-similarity detection — ideal for textual overlap
    - Compare against a local hash index (FAISS-like) of known documents
    
    Output:
    - A similarity score (0–1) indicating degree of duplication
    - Metadata (matched document IDs, similarity ratio)
    """
    
    def __init__(self, db_path: str = "data/clone_detection.db"):
        self.db_path = db_path
        self.simhash_bits = 64
        self.minhash_permutations = 128
        self.shingle_size = 3
        self.similarity_threshold = 0.85
        
        # Initialize database
        self.init_database()
        
        # Pre-generate random permutation functions for MinHash
        self._generate_minhash_functions()
    
    def init_database(self):
        """Initialize enhanced clone detection database with indexing"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced fingerprints table with indexing for fast lookup
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL UNIQUE,
                filename TEXT,
                simhash TEXT NOT NULL,
                minhash_signature TEXT NOT NULL,
                shingles_count INTEGER,
                text_length INTEGER,
                document_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Create indexes for fast similarity search
                FOREIGN KEY (file_id) REFERENCES documents(file_id)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_simhash ON enhanced_fingerprints(simhash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_id ON enhanced_fingerprints(file_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON enhanced_fingerprints(timestamp)')
        
        # Similarity matches table for caching results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS similarity_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_file_id TEXT NOT NULL,
                match_file_id TEXT NOT NULL,
                similarity_score REAL NOT NULL,
                match_method TEXT NOT NULL,
                hamming_distance INTEGER,
                jaccard_similarity REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE(query_file_id, match_file_id, match_method)
            )
        ''')
        
        # Hash index for fast SimHash lookup (LSH-style)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS simhash_buckets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bucket_key TEXT NOT NULL,
                file_id TEXT NOT NULL,
                simhash TEXT NOT NULL,
                
                FOREIGN KEY (file_id) REFERENCES enhanced_fingerprints(file_id)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bucket_key ON simhash_buckets(bucket_key)')
        
        conn.commit()
        conn.close()
    
    def _generate_minhash_functions(self):
        """Pre-generate random hash functions for MinHash"""
        random.seed(42)  # For reproducibility
        self.minhash_functions = []
        
        for _ in range(self.minhash_permutations):
            # Generate random coefficients for hash function: (a*x + b) mod p
            a = random.randint(1, 2**32 - 1)
            b = random.randint(0, 2**32 - 1)
            self.minhash_functions.append((a, b))
    
    def process_document(self, text: str, file_id: str, filename: str = None, 
                        document_type: str = None, auto_train: bool = True) -> Dict[str, Any]:
        """
        Main entry point for Stage 3 clone detection processing with automatic training
        
        Args:
            text: Document text content
            file_id: Unique identifier for the document
            filename: Original filename
            document_type: Type/category of document
            auto_train: Whether to automatically add this document to the training set
        
        Returns:
        {
            'file_id': str,
            'similarity_score': float (0-1),
            'duplicates_found': int,
            'similarity_matches': List[Dict],
            'fingerprint_data': Dict,
            'metadata': Dict,
            'training_status': Dict
        }
        """
        start_time = datetime.now()
        
        # Step 1: Generate comprehensive fingerprints
        fingerprints = self._generate_fingerprints(text, file_id, filename, document_type)
        
        # Step 2: Search for similar documents (before adding to database)
        similarity_matches = self._search_similar_documents(fingerprints)
        
        # Step 3: Calculate overall similarity score
        max_similarity = max([match['similarity_score'] for match in similarity_matches], default=0.0)
        
        # Step 4: Auto-training - Store fingerprints for future clone detection
        training_status = {'trained': False, 'reason': None, 'duplicate_threshold_exceeded': False}
        
        if auto_train:
            training_result = self._auto_train_document(fingerprints, max_similarity)
            training_status.update(training_result)
        
        # Step 5: Cache similarity results for performance
        self._cache_similarity_results(file_id, similarity_matches)
        
        # Step 6: Build response
        result = {
            'file_id': file_id,
            'filename': filename,
            'similarity_score': max_similarity,
            'duplicates_found': len([m for m in similarity_matches if m['similarity_score'] > 0.95]),
            'similarity_matches': similarity_matches,
            'fingerprint_data': {
                'simhash': fingerprints['simhash'],
                'minhash_signature_length': len(fingerprints['minhash_signature']),
                'shingles_count': fingerprints['shingles_count'],
                'text_length': fingerprints['text_length']
            },
            'metadata': {
                'document_type': document_type,
                'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'similarity_threshold': self.similarity_threshold,
                'timestamp': datetime.now().isoformat(),
                'auto_train_enabled': auto_train
            },
            'training_status': training_status
        }
        
        return result
    
    def _generate_fingerprints(self, text: str, file_id: str, filename: str = None, 
                              document_type: str = None) -> Dict[str, Any]:
        """Generate SimHash and MinHash fingerprints"""
        
        # Clean and normalize text
        cleaned_text = self._clean_text(text)
        
        # Generate shingles (n-grams)
        shingles = self._generate_shingles(cleaned_text, self.shingle_size)
        
        # Generate SimHash for approximate similarity
        simhash = self._generate_simhash(shingles)
        
        # Generate MinHash signature for set similarity
        minhash_signature = self._generate_minhash(shingles)
        
        return {
            'file_id': file_id,
            'filename': filename,
            'simhash': simhash,
            'minhash_signature': minhash_signature,
            'shingles': shingles,
            'shingles_count': len(shingles),
            'text_length': len(text),
            'document_type': document_type,
            'timestamp': datetime.now().isoformat()
        }
    
    def _clean_text(self, text: str) -> str:
        """Enhanced text cleaning and normalization"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but preserve word boundaries
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove very short words (less than 3 characters)
        words = [word for word in text.split() if len(word) >= 3]
        
        return ' '.join(words)
    
    def _generate_shingles(self, text: str, n: int) -> List[str]:
        """Generate n-gram shingles with improved tokenization"""
        words = text.split()
        
        if len(words) < n:
            return [text]  # Return the whole text if it's shorter than n
        
        shingles = []
        for i in range(len(words) - n + 1):
            shingle = ' '.join(words[i:i+n])
            shingles.append(shingle)
        
        return list(set(shingles))  # Remove duplicates
    
    def _generate_simhash(self, shingles: List[str]) -> str:
        """
        Generate SimHash for approximate similarity detection
        Uses feature hashing with weighted bit vectors
        """
        if not shingles:
            return "0" * self.simhash_bits
        
        # Initialize bit vector
        v = [0.0] * self.simhash_bits
        
        for shingle in shingles:
            # Generate hash for this shingle
            hash_value = int(hashlib.md5(shingle.encode('utf-8')).hexdigest(), 16)
            
            # Weight based on shingle frequency (if we had counts)
            weight = 1.0
            
            # Update bit vector
            for i in range(self.simhash_bits):
                if hash_value & (1 << i):
                    v[i] += weight
                else:
                    v[i] -= weight
        
        # Generate final SimHash
        simhash = 0
        for i in range(self.simhash_bits):
            if v[i] > 0:
                simhash |= (1 << i)
        
        return format(simhash, f'0{self.simhash_bits}b')
    
    def _generate_minhash(self, shingles: List[str]) -> List[int]:
        """
        Generate MinHash signature for set similarity (Jaccard similarity)
        """
        if not shingles:
            return [0] * self.minhash_permutations
        
        # Convert shingles to hash values
        shingle_hashes = set()
        for shingle in shingles:
            shingle_hash = int(hashlib.md5(shingle.encode('utf-8')).hexdigest(), 16) % (2**32)
            shingle_hashes.add(shingle_hash)
        
        # Generate MinHash signature
        signature = []
        prime = 2**61 - 1  # Large prime for modular arithmetic
        
        for a, b in self.minhash_functions:
            min_hash = float('inf')
            for shingle_hash in shingle_hashes:
                # Apply hash function: (a * x + b) mod prime
                hash_val = (a * shingle_hash + b) % prime
                min_hash = min(min_hash, hash_val)
            
            signature.append(int(min_hash) if min_hash != float('inf') else 0)
        
        return signature
    
    def _search_similar_documents(self, query_fingerprints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for similar documents using both SimHash and MinHash
        """
        similar_docs = []
        
        # Search using SimHash (fast approximate similarity)
        simhash_matches = self._search_by_simhash(query_fingerprints['simhash'])
        
        # Search using MinHash (precise set similarity)
        minhash_matches = self._search_by_minhash(query_fingerprints['minhash_signature'])
        
        # Combine and deduplicate results
        all_matches = {}
        
        # Process SimHash matches
        for match in simhash_matches:
            file_id = match['file_id']
            all_matches[file_id] = {
                'file_id': file_id,
                'filename': match['filename'],
                'similarity_score': match['similarity_score'],
                'match_method': 'simhash',
                'hamming_distance': match['hamming_distance'],
                'jaccard_similarity': None,
                'match_details': {
                    'simhash_similarity': match['similarity_score'],
                    'hamming_distance': match['hamming_distance']
                }
            }
        
        # Process MinHash matches (update existing or add new)
        for match in minhash_matches:
            file_id = match['file_id']
            if file_id in all_matches:
                # Update with MinHash data
                all_matches[file_id]['jaccard_similarity'] = match['jaccard_similarity']
                all_matches[file_id]['match_details']['jaccard_similarity'] = match['jaccard_similarity']
                # Use the maximum similarity score
                all_matches[file_id]['similarity_score'] = max(
                    all_matches[file_id]['similarity_score'],
                    match['jaccard_similarity']
                )
                all_matches[file_id]['match_method'] = 'combined'
            else:
                all_matches[file_id] = {
                    'file_id': file_id,
                    'filename': match['filename'],
                    'similarity_score': match['jaccard_similarity'],
                    'match_method': 'minhash',
                    'hamming_distance': None,
                    'jaccard_similarity': match['jaccard_similarity'],
                    'match_details': {
                        'jaccard_similarity': match['jaccard_similarity']
                    }
                }
        
        # Convert to list and sort by similarity
        similar_docs = list(all_matches.values())
        similar_docs.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Filter by threshold
        similar_docs = [doc for doc in similar_docs if doc['similarity_score'] >= self.similarity_threshold]
        
        return similar_docs
    
    def _search_by_simhash(self, query_simhash: str) -> List[Dict[str, Any]]:
        """Search for similar documents using SimHash with Hamming distance"""
        matches = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all stored SimHashes
        cursor.execute('SELECT file_id, filename, simhash FROM enhanced_fingerprints')
        results = cursor.fetchall()
        
        query_int = int(query_simhash, 2)
        
        for file_id, filename, stored_simhash in results:
            if stored_simhash and stored_simhash != query_simhash:  # Exclude exact self-matches
                try:
                    stored_int = int(stored_simhash, 2)
                    
                    # Calculate Hamming distance
                    hamming_distance = bin(query_int ^ stored_int).count('1')
                    
                    # Convert to similarity score (closer to 1 = more similar)
                    similarity_score = 1.0 - (hamming_distance / self.simhash_bits)
                    
                    # Only include if above threshold
                    if similarity_score >= self.similarity_threshold:
                        matches.append({
                            'file_id': file_id,
                            'filename': filename,
                            'similarity_score': similarity_score,
                            'hamming_distance': hamming_distance
                        })
                except (ValueError, TypeError):
                    continue
        
        conn.close()
        return matches
    
    def _search_by_minhash(self, query_minhash: List[int]) -> List[Dict[str, Any]]:
        """Search for similar documents using MinHash with Jaccard similarity"""
        matches = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all stored MinHash signatures
        cursor.execute('SELECT file_id, filename, minhash_signature FROM enhanced_fingerprints')
        results = cursor.fetchall()
        
        for file_id, filename, stored_minhash_str in results:
            if stored_minhash_str:
                try:
                    stored_minhash = json.loads(stored_minhash_str)
                    
                    # Skip if same signature (self-match)
                    if stored_minhash == query_minhash:
                        continue
                    
                    # Calculate Jaccard similarity estimate
                    jaccard_similarity = self._estimate_jaccard_similarity(query_minhash, stored_minhash)
                    
                    # Only include if above threshold
                    if jaccard_similarity >= self.similarity_threshold:
                        matches.append({
                            'file_id': file_id,
                            'filename': filename,
                            'jaccard_similarity': jaccard_similarity
                        })
                except (json.JSONDecodeError, TypeError):
                    continue
        
        conn.close()
        return matches
    
    def _estimate_jaccard_similarity(self, sig1: List[int], sig2: List[int]) -> float:
        """Estimate Jaccard similarity from MinHash signatures"""
        if len(sig1) != len(sig2):
            return 0.0
        
        matches = sum(1 for i in range(len(sig1)) if sig1[i] == sig2[i])
        return matches / len(sig1)
    
    def _store_fingerprints(self, fingerprints: Dict[str, Any]):
        """Store fingerprints in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store main fingerprint data
        cursor.execute('''
            INSERT OR REPLACE INTO enhanced_fingerprints 
            (file_id, filename, simhash, minhash_signature, shingles_count, text_length, document_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            fingerprints['file_id'],
            fingerprints['filename'],
            fingerprints['simhash'],
            json.dumps(fingerprints['minhash_signature']),
            fingerprints['shingles_count'],
            fingerprints['text_length'],
            fingerprints['document_type']
        ))
        
        # Store SimHash buckets for LSH-style fast lookup (optional optimization)
        self._store_simhash_buckets(cursor, fingerprints['file_id'], fingerprints['simhash'])
        
        conn.commit()
        conn.close()
    
    def _store_simhash_buckets(self, cursor, file_id: str, simhash: str):
        """Store SimHash in buckets for fast LSH-style lookup"""
        # Create multiple bucket keys by masking different parts of the SimHash
        bucket_size = 16  # bits per bucket
        num_buckets = self.simhash_bits // bucket_size
        
        for i in range(num_buckets):
            start_bit = i * bucket_size
            end_bit = start_bit + bucket_size
            bucket_key = simhash[start_bit:end_bit]
            
            cursor.execute('''
                INSERT OR REPLACE INTO simhash_buckets (bucket_key, file_id, simhash)
                VALUES (?, ?, ?)
            ''', (bucket_key, file_id, simhash))
    
    def _auto_train_document(self, fingerprints: Dict[str, Any], max_similarity: float) -> Dict[str, Any]:
        """
        Automatically train the system on this document for future clone detection
        
        Args:
            fingerprints: Generated fingerprints for the document
            max_similarity: Highest similarity score found with existing documents
            
        Returns:
            Dictionary with training status and metadata
        """
        training_result = {
            'trained': False,
            'reason': None,
            'duplicate_threshold_exceeded': False,
            'existing_document_updated': False,
            'training_timestamp': datetime.now().isoformat()
        }
        
        # Check if this is a near-duplicate (very high similarity)
        duplicate_threshold = 0.95
        if max_similarity >= duplicate_threshold:
            training_result['duplicate_threshold_exceeded'] = True
            training_result['reason'] = f'Document too similar to existing (similarity: {max_similarity:.3f})'
            
            # Option 1: Don't train on near-duplicates to avoid polluting the training set
            # Option 2: Update existing document metadata instead
            
            # We'll update the existing similar document's metadata
            self._update_similar_document_metadata(fingerprints, max_similarity)
            training_result['existing_document_updated'] = True
            
            return training_result
        
        # Check if document meets minimum quality criteria for training
        min_text_length = 50  # Minimum characters
        min_shingles = 5      # Minimum shingles for meaningful fingerprints
        
        if fingerprints['text_length'] < min_text_length:
            training_result['reason'] = f'Document too short for training ({fingerprints["text_length"]} chars)'
            return training_result
            
        if fingerprints['shingles_count'] < min_shingles:
            training_result['reason'] = f'Too few shingles for training ({fingerprints["shingles_count"]} shingles)'
            return training_result
        
        # Check if file_id already exists (avoid duplicate training)
        if self._document_already_trained(fingerprints['file_id']):
            training_result['reason'] = 'Document already in training set'
            training_result['existing_document_updated'] = True
            # Update the existing entry with new data
            self._store_fingerprints(fingerprints)
            training_result['trained'] = True
            return training_result
        
        # All checks passed - train on this document
        try:
            self._store_fingerprints(fingerprints)
            self._log_training_event(fingerprints)
            
            training_result['trained'] = True
            training_result['reason'] = 'Document successfully added to training set'
            
        except Exception as e:
            training_result['reason'] = f'Training failed: {str(e)}'
        
        return training_result
    
    def _document_already_trained(self, file_id: str) -> bool:
        """Check if a document is already in the training set"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM enhanced_fingerprints WHERE file_id = ?', (file_id,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0
    
    def _update_similar_document_metadata(self, fingerprints: Dict[str, Any], similarity_score: float):
        """Update metadata for similar documents instead of adding duplicates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find the most similar document
        similar_docs = self._search_similar_documents(fingerprints)
        if similar_docs:
            most_similar = similar_docs[0]
            
            # Log this as a duplicate encounter
            cursor.execute('''
                INSERT OR REPLACE INTO similarity_matches
                (query_file_id, match_file_id, similarity_score, match_method, created_at)
                VALUES (?, ?, ?, 'duplicate_encounter', ?)
            ''', (
                fingerprints['file_id'],
                most_similar['file_id'],
                similarity_score,
                datetime.now().isoformat()
            ))
            
        conn.commit()
        conn.close()
    
    def _log_training_event(self, fingerprints: Dict[str, Any]):
        """Log training events for monitoring and analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create training log table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                filename TEXT,
                document_type TEXT,
                text_length INTEGER,
                shingles_count INTEGER,
                training_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                training_method TEXT DEFAULT 'auto_train'
            )
        ''')
        
        # Log this training event
        cursor.execute('''
            INSERT INTO training_log 
            (file_id, filename, document_type, text_length, shingles_count, training_method)
            VALUES (?, ?, ?, ?, ?, 'auto_train_stage3')
        ''', (
            fingerprints['file_id'],
            fingerprints['filename'],
            fingerprints['document_type'],
            fingerprints['text_length'],
            fingerprints['shingles_count']
        ))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get clone detection statistics including training metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count total fingerprints
        cursor.execute('SELECT COUNT(*) FROM enhanced_fingerprints')
        total_fingerprints = cursor.fetchone()[0]
        
        # Count similarity matches
        cursor.execute('SELECT COUNT(*) FROM similarity_matches')
        total_matches = cursor.fetchone()[0]
        
        # Get average similarity scores
        cursor.execute('SELECT AVG(similarity_score) FROM similarity_matches')
        avg_similarity = cursor.fetchone()[0] or 0.0
        
        # Get method distribution
        cursor.execute('''
            SELECT match_method, COUNT(*) 
            FROM similarity_matches 
            GROUP BY match_method
        ''')
        method_distribution = dict(cursor.fetchall())
        
        # Get training statistics
        training_stats = self._get_training_statistics(cursor)
        
        # Get document type distribution
        cursor.execute('''
            SELECT document_type, COUNT(*) 
            FROM enhanced_fingerprints 
            GROUP BY document_type
        ''')
        document_type_distribution = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_fingerprints': total_fingerprints,
            'total_similarity_matches': total_matches,
            'average_similarity_score': round(avg_similarity, 3),
            'method_distribution': method_distribution,
            'document_type_distribution': document_type_distribution,
            'training_statistics': training_stats,
            'simhash_bits': self.simhash_bits,
            'minhash_permutations': self.minhash_permutations,
            'similarity_threshold': self.similarity_threshold
        }
    
    def _get_training_statistics(self, cursor) -> Dict[str, Any]:
        """Get detailed training statistics"""
        stats = {}
        
        # Check if training_log table exists
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='training_log'
        ''')
        
        if cursor.fetchone():
            # Total training events
            cursor.execute('SELECT COUNT(*) FROM training_log')
            stats['total_training_events'] = cursor.fetchone()[0]
            
            # Training events by method
            cursor.execute('''
                SELECT training_method, COUNT(*) 
                FROM training_log 
                GROUP BY training_method
            ''')
            stats['training_by_method'] = dict(cursor.fetchall())
            
            # Recent training activity (last 24 hours)
            cursor.execute('''
                SELECT COUNT(*) FROM training_log 
                WHERE training_timestamp > datetime('now', '-1 day')
            ''')
            stats['recent_training_events'] = cursor.fetchone()[0]
            
            # Average document characteristics
            cursor.execute('''
                SELECT 
                    AVG(text_length) as avg_text_length,
                    AVG(shingles_count) as avg_shingles_count
                FROM training_log
            ''')
            row = cursor.fetchone()
            if row:
                stats['average_text_length'] = round(row[0] or 0, 1)
                stats['average_shingles_count'] = round(row[1] or 0, 1)
        else:
            stats = {
                'total_training_events': 0,
                'training_by_method': {},
                'recent_training_events': 0,
                'average_text_length': 0,
                'average_shingles_count': 0
            }
        
        return stats
    
    def get_training_quality_metrics(self) -> Dict[str, Any]:
        """Get metrics about training data quality"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Text length distribution
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN text_length < 100 THEN 1 END) as very_short,
                COUNT(CASE WHEN text_length BETWEEN 100 AND 500 THEN 1 END) as short,
                COUNT(CASE WHEN text_length BETWEEN 500 AND 2000 THEN 1 END) as medium,
                COUNT(CASE WHEN text_length > 2000 THEN 1 END) as long
            FROM enhanced_fingerprints
        ''')
        length_dist = cursor.fetchone()
        
        # Shingle count distribution
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN shingles_count < 10 THEN 1 END) as few_shingles,
                COUNT(CASE WHEN shingles_count BETWEEN 10 AND 50 THEN 1 END) as moderate_shingles,
                COUNT(CASE WHEN shingles_count > 50 THEN 1 END) as many_shingles
            FROM enhanced_fingerprints
        ''')
        shingle_dist = cursor.fetchone()
        
        # Duplicate detection rate
        cursor.execute('''
            SELECT COUNT(*) FROM similarity_matches 
            WHERE match_method = 'duplicate_encounter'
        ''')
        duplicate_encounters = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'text_length_distribution': {
                'very_short_docs': length_dist[0],
                'short_docs': length_dist[1], 
                'medium_docs': length_dist[2],
                'long_docs': length_dist[3]
            },
            'shingle_distribution': {
                'few_shingles': shingle_dist[0],
                'moderate_shingles': shingle_dist[1],
                'many_shingles': shingle_dist[2]
            },
            'duplicate_encounters': duplicate_encounters,
            'training_data_quality': self._assess_training_quality(length_dist, shingle_dist)
        }
    
    def _assess_training_quality(self, length_dist, shingle_dist) -> str:
        """Assess overall training data quality"""
        total_docs = sum(length_dist)
        if total_docs == 0:
            return "No training data"
        
        # Calculate quality score based on document characteristics
        quality_score = 0
        
        # Prefer medium to long documents
        quality_score += (length_dist[2] + length_dist[3]) / total_docs * 0.4
        
        # Prefer documents with moderate to many shingles
        total_shingle_docs = sum(shingle_dist)
        if total_shingle_docs > 0:
            quality_score += (shingle_dist[1] + shingle_dist[2]) / total_shingle_docs * 0.6
        
        if quality_score >= 0.8:
            return "Excellent"
        elif quality_score >= 0.6:
            return "Good" 
        elif quality_score >= 0.4:
            return "Fair"
        else:
            return "Poor"
    
    def remove_document_from_training(self, file_id: str) -> Dict[str, Any]:
        """Remove a document from the training set"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if document exists
        cursor.execute('SELECT filename FROM enhanced_fingerprints WHERE file_id = ?', (file_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return {'success': False, 'reason': 'Document not found in training set'}
        
        filename = result[0]
        
        try:
            # Remove fingerprints
            cursor.execute('DELETE FROM enhanced_fingerprints WHERE file_id = ?', (file_id,))
            
            # Remove similarity matches
            cursor.execute('''
                DELETE FROM similarity_matches 
                WHERE query_file_id = ? OR match_file_id = ?
            ''', (file_id, file_id))
            
            # Remove from buckets
            cursor.execute('DELETE FROM simhash_buckets WHERE file_id = ?', (file_id,))
            
            # Log removal
            cursor.execute('''
                INSERT INTO training_log 
                (file_id, filename, training_method, training_timestamp)
                VALUES (?, ?, 'removed_from_training', ?)
            ''', (file_id, filename, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True, 
                'message': f'Document {filename} removed from training set',
                'file_id': file_id
            }
            
        except Exception as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'reason': f'Removal failed: {str(e)}'}
    
    def _cache_similarity_results(self, query_file_id: str, matches: List[Dict[str, Any]]):
        """Cache similarity results for performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for match in matches:
            cursor.execute('''
                INSERT OR REPLACE INTO similarity_matches
                (query_file_id, match_file_id, similarity_score, match_method, 
                 hamming_distance, jaccard_similarity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                query_file_id,
                match['file_id'],
                match['similarity_score'],
                match['match_method'],
                match.get('hamming_distance'),
                match.get('jaccard_similarity')
            ))
        
        conn.commit()
        conn.close()
    
    def update_similarity_threshold(self, new_threshold: float):
        """Update similarity threshold for future searches"""
        if 0.0 <= new_threshold <= 1.0:
            self.similarity_threshold = new_threshold
        else:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")


# Global service instance
enhanced_clone_detection_service = EnhancedCloneDetectionService()
