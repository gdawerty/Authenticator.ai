"""
Fingerprint & Clone Detection Service
Implements text shingles+SimHash+dense embeddings, image pHash/dHash+CLIP, and document template hashes
"""

import hashlib
import numpy as np
import imagehash
from PIL import Image
from io import BytesIO
import sqlite3
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import re


class FingerprintService:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '../data/clone_detection.db')
        self.init_database()

    def init_database(self):
        """Initialize clone detection database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Text fingerprints table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS text_fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                filename TEXT,
                simhash TEXT,
                shingles TEXT,
                embedding_hash TEXT,
                text_length INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file_id)
            )
        ''')

        # Image fingerprints table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                filename TEXT,
                phash TEXT,
                dhash TEXT,
                ahash TEXT,
                whash TEXT,
                clip_hash TEXT,
                image_size TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file_id)
            )
        ''')

        # Document template fingerprints
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                filename TEXT,
                template_hash TEXT,
                structure_hash TEXT,
                layout_features TEXT,
                document_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file_id)
            )
        ''')

        # Verified originals table (high authenticity documents)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verified_originals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                filename TEXT,
                authenticity_score REAL,
                document_type TEXT,
                bert_confidence REAL,
                vit_confidence REAL,
                verification_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'verified_original',
                UNIQUE(file_id)
            )
        ''')

        # Training metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                training_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                text_fingerprint_added BOOLEAN DEFAULT FALSE,
                image_fingerprint_added BOOLEAN DEFAULT FALSE,
                document_fingerprint_added BOOLEAN DEFAULT FALSE,
                authenticity_score REAL,
                document_type TEXT,
                training_session_id TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def generate_text_fingerprint(self, text: str, file_id: str, filename: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive text fingerprint using shingles, SimHash, and dense embeddings
        """
        if not text or len(text.strip()) < 10:
            return {
                'file_id': file_id,
                'simhash': None,
                'shingles': [],
                'embedding_hash': None,
                'text_length': 0,
                'duplicates': []
            }

        # Clean text
        cleaned_text = self._clean_text(text)

        # Generate shingles (n-grams)
        shingles = self._generate_shingles(cleaned_text, n=3)

        # Generate SimHash
        simhash = self._generate_simhash(shingles)

        # Generate embedding hash (simplified - would use actual embeddings in production)
        embedding_hash = self._generate_embedding_hash(cleaned_text)

        fingerprint = {
            'file_id': file_id,
            'filename': filename,
            'simhash': simhash,
            'shingles': shingles[:100],  # Store first 100 shingles
            'embedding_hash': embedding_hash,
            'text_length': len(text),
            'created_at': datetime.now().isoformat()
        }

        # Find duplicates
        duplicates = self._find_text_duplicates(simhash, embedding_hash, shingles)
        fingerprint['duplicates'] = duplicates

        # Store in database
        self._store_text_fingerprint(fingerprint)

        return fingerprint

    def generate_image_fingerprint(self, image_bytes: bytes, file_id: str, filename: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive image fingerprint using pHash, dHash, aHash, wHash
        """
        try:
            # Load image
            image = Image.open(BytesIO(image_bytes))

            # Generate various hashes
            phash = str(imagehash.phash(image))
            dhash = str(imagehash.dhash(image))
            ahash = str(imagehash.average_hash(image))
            whash = str(imagehash.whash(image))

            # Generate CLIP-style hash (simplified)
            clip_hash = self._generate_clip_hash(image)

            fingerprint = {
                'file_id': file_id,
                'filename': filename,
                'phash': phash,
                'dhash': dhash,
                'ahash': ahash,
                'whash': whash,
                'clip_hash': clip_hash,
                'image_size': f"{image.width}x{image.height}",
                'created_at': datetime.now().isoformat()
            }

            # Find duplicates
            duplicates = self._find_image_duplicates(phash, dhash, ahash, whash, clip_hash)
            fingerprint['duplicates'] = duplicates

            # Store in database
            self._store_image_fingerprint(fingerprint)

            return fingerprint

        except Exception as e:
            return {
                'file_id': file_id,
                'error': f'Image fingerprinting failed: {str(e)}',
                'duplicates': []
            }

    def generate_document_fingerprint(self, text: str, file_id: str, filename: str = None, doc_type: str = None) -> Dict[str, Any]:
        """
        Generate document template fingerprint for layout and structure analysis
        """
        # Generate template hash based on structure
        template_hash = self._generate_template_hash(text)

        # Analyze document structure
        structure_hash = self._generate_structure_hash(text)

        # Extract layout features
        layout_features = self._extract_layout_features(text)

        fingerprint = {
            'file_id': file_id,
            'filename': filename,
            'template_hash': template_hash,
            'structure_hash': structure_hash,
            'layout_features': json.dumps(layout_features),
            'document_type': doc_type or 'unknown',
            'created_at': datetime.now().isoformat()
        }

        # Find template duplicates
        duplicates = self._find_template_duplicates(template_hash, structure_hash)
        fingerprint['duplicates'] = duplicates

        # Store in database
        self._store_document_fingerprint(fingerprint)

        return fingerprint

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for fingerprinting"""
        # Remove extra whitespace, normalize case
        text = re.sub(r'\s+', ' ', text.lower().strip())
        # Remove special characters but keep structure
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-]', '', text)
        return text

    def _generate_shingles(self, text: str, n: int = 3) -> List[str]:
        """Generate n-gram shingles from text"""
        words = text.split()
        shingles = []
        for i in range(len(words) - n + 1):
            shingle = ' '.join(words[i:i+n])
            shingles.append(shingle)
        return shingles

    def _generate_simhash(self, shingles: List[str]) -> str:
        """Generate SimHash from shingles"""
        if not shingles:
            return "0" * 64

        hash_bits = 64
        v = [0] * hash_bits

        for shingle in shingles:
            # Hash the shingle
            h = hashlib.md5(shingle.encode()).hexdigest()
            h_int = int(h, 16)

            # Update vector
            for i in range(hash_bits):
                if h_int & (1 << i):
                    v[i] += 1
                else:
                    v[i] -= 1

        # Generate final hash
        simhash = 0
        for i in range(hash_bits):
            if v[i] > 0:
                simhash |= (1 << i)

        return format(simhash, '064b')

    def _generate_embedding_hash(self, text: str) -> str:
        """Generate hash from text embeddings (simplified version)"""
        # In production, this would use actual embeddings (BERT, sentence-transformers, etc.)
        # For now, use a combination of text features
        features = [
            len(text),
            len(text.split()),
            len(set(text.split())),  # unique words
            text.count('.'),
            text.count(','),
            text.count('!'),
            text.count('?')
        ]

        feature_str = '-'.join(map(str, features))
        return hashlib.sha256(feature_str.encode()).hexdigest()[:16]

    def _generate_clip_hash(self, image: Image.Image) -> str:
        """Generate CLIP-style hash (simplified)"""
        # In production, this would use actual CLIP embeddings
        # For now, use image statistics
        arr = np.array(image.convert('RGB'))
        features = [
            int(arr.mean()),
            int(arr.std()),
            int(arr.min()),
            int(arr.max()),
            image.width,
            image.height
        ]

        feature_str = '-'.join(map(str, features))
        return hashlib.sha256(feature_str.encode()).hexdigest()[:16]

    def _generate_template_hash(self, text: str) -> str:
        """Generate template hash based on document structure"""
        # Extract structural elements
        lines = text.split('\n')
        structure_patterns = []

        for line in lines:
            line = line.strip()
            if not line:
                structure_patterns.append('EMPTY')
            elif line.isupper():
                structure_patterns.append('HEADER')
            elif line.endswith(':'):
                structure_patterns.append('LABEL')
            elif any(char.isdigit() for char in line):
                structure_patterns.append('DATA')
            else:
                structure_patterns.append('TEXT')

        pattern_str = '-'.join(structure_patterns)
        return hashlib.sha256(pattern_str.encode()).hexdigest()[:16]

    def _generate_structure_hash(self, text: str) -> str:
        """Generate hash based on document structure patterns"""
        # Analyze paragraph structure, headers, lists, etc.
        structure_features = {
            'paragraphs': len(text.split('\n\n')),
            'lines': len(text.split('\n')),
            'bullets': text.count('•') + text.count('-') + text.count('*'),
            'numbers': len(re.findall(r'\d+\.', text)),
            'headers': len(re.findall(r'^[A-Z][A-Z\s]+$', text, re.MULTILINE))
        }

        feature_str = json.dumps(structure_features, sort_keys=True)
        return hashlib.sha256(feature_str.encode()).hexdigest()[:16]

    def _extract_layout_features(self, text: str) -> Dict[str, Any]:
        """Extract layout and formatting features"""
        return {
            'total_length': len(text),
            'word_count': len(text.split()),
            'line_count': len(text.split('\n')),
            'paragraph_count': len(text.split('\n\n')),
            'avg_line_length': len(text) / max(1, len(text.split('\n'))),
            'avg_word_length': len(text.replace(' ', '')) / max(1, len(text.split())),
            'punctuation_density': sum(1 for c in text if c in '.,!?;:') / max(1, len(text)),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / max(1, len(text)),
            'digit_ratio': sum(1 for c in text if c.isdigit()) / max(1, len(text))
        }

    def _find_text_duplicates(self, simhash: str, embedding_hash: str, shingles: List[str]) -> List[Dict[str, Any]]:
        """Find text duplicates using SimHash and embedding similarity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT file_id, filename, simhash, embedding_hash, shingles FROM text_fingerprints')
        results = cursor.fetchall()

        duplicates = []
        for row in results:
            existing_file_id, existing_filename, existing_simhash, existing_embedding_hash, existing_shingles = row

            # Calculate SimHash distance (Hamming distance)
            if existing_simhash and simhash:
                simhash_distance = bin(int(simhash, 2) ^ int(existing_simhash, 2)).count('1')
                similarity_score = 1.0 - (simhash_distance / 64.0)

                # Consider as duplicate if similarity > 0.85
                if similarity_score > 0.85:
                    duplicates.append({
                        'file_id': existing_file_id,
                        'filename': existing_filename,
                        'similarity_score': similarity_score,
                        'match_type': 'simhash',
                        'distance': simhash_distance
                    })

            # Check embedding hash exact match
            if existing_embedding_hash == embedding_hash:
                duplicates.append({
                    'file_id': existing_file_id,
                    'filename': existing_filename,
                    'similarity_score': 1.0,
                    'match_type': 'embedding_exact',
                    'distance': 0
                })

        conn.close()
        return duplicates

    def _find_image_duplicates(self, phash: str, dhash: str, ahash: str, whash: str, clip_hash: str) -> List[Dict[str, Any]]:
        """Find image duplicates using perceptual hashes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT file_id, filename, phash, dhash, ahash, whash, clip_hash FROM image_fingerprints')
        results = cursor.fetchall()

        duplicates = []
        for row in results:
            existing_file_id, existing_filename, existing_phash, existing_dhash, existing_ahash, existing_whash, existing_clip_hash = row

            # Calculate hash distances
            hash_distances = {}
            if existing_phash and phash:
                hash_distances['phash'] = bin(int(phash, 16) ^ int(existing_phash, 16)).count('1')
            if existing_dhash and dhash:
                hash_distances['dhash'] = bin(int(dhash, 16) ^ int(existing_dhash, 16)).count('1')
            if existing_ahash and ahash:
                hash_distances['ahash'] = bin(int(ahash, 16) ^ int(existing_ahash, 16)).count('1')
            if existing_whash and whash:
                hash_distances['whash'] = bin(int(whash, 16) ^ int(existing_whash, 16)).count('1')

            # Find minimum distance
            if hash_distances:
                min_distance = min(hash_distances.values())
                similarity_score = 1.0 - (min_distance / 64.0)

                # Consider as duplicate if similarity > 0.9
                if similarity_score > 0.9:
                    duplicates.append({
                        'file_id': existing_file_id,
                        'filename': existing_filename,
                        'similarity_score': similarity_score,
                        'match_type': 'perceptual_hash',
                        'distances': hash_distances
                    })

            # Check CLIP hash exact match
            if existing_clip_hash == clip_hash:
                duplicates.append({
                    'file_id': existing_file_id,
                    'filename': existing_filename,
                    'similarity_score': 1.0,
                    'match_type': 'clip_exact',
                    'distance': 0
                })

        conn.close()
        return duplicates

    def _find_template_duplicates(self, template_hash: str, structure_hash: str) -> List[Dict[str, Any]]:
        """Find document template duplicates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT file_id, filename, template_hash, structure_hash FROM document_fingerprints')
        results = cursor.fetchall()

        duplicates = []
        for row in results:
            existing_file_id, existing_filename, existing_template_hash, existing_structure_hash = row

            # Check exact template match
            if existing_template_hash == template_hash:
                duplicates.append({
                    'file_id': existing_file_id,
                    'filename': existing_filename,
                    'similarity_score': 1.0,
                    'match_type': 'template_exact'
                })

            # Check structure match
            elif existing_structure_hash == structure_hash:
                duplicates.append({
                    'file_id': existing_file_id,
                    'filename': existing_filename,
                    'similarity_score': 0.85,
                    'match_type': 'structure_match'
                })

        conn.close()
        return duplicates

    def _store_text_fingerprint(self, fingerprint: Dict[str, Any]):
        """Store text fingerprint in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO text_fingerprints
            (file_id, filename, simhash, shingles, embedding_hash, text_length)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            fingerprint['file_id'],
            fingerprint['filename'],
            fingerprint['simhash'],
            json.dumps(fingerprint['shingles']),
            fingerprint['embedding_hash'],
            fingerprint['text_length']
        ))

        conn.commit()
        conn.close()

    def _store_image_fingerprint(self, fingerprint: Dict[str, Any]):
        """Store image fingerprint in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO image_fingerprints
            (file_id, filename, phash, dhash, ahash, whash, clip_hash, image_size)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            fingerprint['file_id'],
            fingerprint['filename'],
            fingerprint['phash'],
            fingerprint['dhash'],
            fingerprint['ahash'],
            fingerprint['whash'],
            fingerprint['clip_hash'],
            fingerprint['image_size']
        ))

        conn.commit()
        conn.close()

    def _store_document_fingerprint(self, fingerprint: Dict[str, Any]):
        """Store document fingerprint in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO document_fingerprints
            (file_id, filename, template_hash, structure_hash, layout_features, document_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            fingerprint['file_id'],
            fingerprint['filename'],
            fingerprint['template_hash'],
            fingerprint['structure_hash'],
            fingerprint['layout_features'],
            fingerprint['document_type']
        ))

        conn.commit()
        conn.close()

    def get_clone_statistics(self) -> Dict[str, Any]:
        """Get clone detection database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Text fingerprints stats
        cursor.execute('SELECT COUNT(*) FROM text_fingerprints')
        stats['total_text_fingerprints'] = cursor.fetchone()[0]

        # Image fingerprints stats
        cursor.execute('SELECT COUNT(*) FROM image_fingerprints')
        stats['total_image_fingerprints'] = cursor.fetchone()[0]

        # Document fingerprints stats
        cursor.execute('SELECT COUNT(*) FROM document_fingerprints')
        stats['total_document_fingerprints'] = cursor.fetchone()[0]

        # Verified originals stats
        try:
            cursor.execute('SELECT COUNT(*) FROM verified_originals')
            stats['total_verified_originals'] = cursor.fetchone()[0]
        except:
            stats['total_verified_originals'] = 0

        # Training metadata stats
        try:
            cursor.execute('SELECT COUNT(*) FROM training_metadata')
            stats['total_training_sessions'] = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM training_metadata WHERE training_timestamp >= datetime("now", "-24 hours")')
            stats['training_sessions_last_24h'] = cursor.fetchone()[0]
        except:
            stats['total_training_sessions'] = 0
            stats['training_sessions_last_24h'] = 0

        # Calculate total fingerprints
        stats['total_fingerprints'] = (
            stats['total_text_fingerprints'] +
            stats['total_image_fingerprints'] +
            stats['total_document_fingerprints']
        )

        # Self-training effectiveness
        stats['clone_detection_coverage'] = {
            'documents_trained': stats['total_fingerprints'],
            'verified_originals': stats['total_verified_originals'],
            'training_velocity': stats['training_sessions_last_24h']
        }

        conn.close()
        return stats