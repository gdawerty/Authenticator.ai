"""
Cryptographic Integration Service for Authenticator.AI
Implements SHA-256 hashing, digital signature verification, and blockchain anchoring
"""

import hashlib
import hmac
import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64
import requests

class CryptographicService:
    """
    Service for cryptographic operations including hashing, digital signatures,
    and blockchain anchoring for document authenticity verification
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'crypto_audit.db')
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize cryptographic audit database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Document hashes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_hashes (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    sha256_hash TEXT NOT NULL,
                    sha1_hash TEXT,
                    md5_hash TEXT,
                    file_size INTEGER,
                    mime_type TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for document_hashes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_hashes_user_id ON document_hashes(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_hashes_document_id ON document_hashes(document_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_hashes_sha256 ON document_hashes(sha256_hash)')
            
            # Digital signatures table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS digital_signatures (
                    id TEXT PRIMARY KEY,
                    document_hash_id TEXT NOT NULL,
                    signature_algorithm TEXT NOT NULL,
                    signature_data TEXT NOT NULL,
                    public_key TEXT,
                    certificate_chain TEXT,
                    signer_identity TEXT,
                    signature_timestamp DATETIME,
                    verification_status TEXT DEFAULT 'pending',
                    verification_details TEXT DEFAULT '{}',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_hash_id) REFERENCES document_hashes (id)
                )
            ''')
            
            # Blockchain anchors table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blockchain_anchors (
                    id TEXT PRIMARY KEY,
                    document_hash_id TEXT NOT NULL,
                    blockchain_network TEXT NOT NULL,
                    transaction_hash TEXT,
                    block_number INTEGER,
                    block_timestamp DATETIME,
                    anchor_data TEXT NOT NULL,
                    gas_used INTEGER,
                    transaction_fee REAL,
                    confirmation_status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_hash_id) REFERENCES document_hashes (id)
                )
            ''')
            
            # Crypto audit log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crypto_audit_log (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    document_id TEXT,
                    operation_type TEXT NOT NULL,
                    operation_details TEXT NOT NULL,
                    result_status TEXT NOT NULL,
                    error_message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for crypto_audit_log
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user_id ON crypto_audit_log(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_operation ON crypto_audit_log(operation_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON crypto_audit_log(timestamp)')
            
            conn.commit()
    
    def calculate_document_hashes(self, file_content: bytes, filename: str, 
                                user_id: str, document_id: str, mime_type: str = None) -> Dict[str, Any]:
        """Calculate multiple hash algorithms for document"""
        import uuid
        
        hash_id = str(uuid.uuid4())
        
        # Calculate hashes
        sha256_hash = hashlib.sha256(file_content).hexdigest()
        sha1_hash = hashlib.sha1(file_content).hexdigest()
        md5_hash = hashlib.md5(file_content).hexdigest()
        file_size = len(file_content)
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO document_hashes (
                    id, user_id, document_id, filename, sha256_hash, 
                    sha1_hash, md5_hash, file_size, mime_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (hash_id, user_id, document_id, filename, sha256_hash, 
                  sha1_hash, md5_hash, file_size, mime_type))
        
        # Log operation
        self._log_crypto_operation(
            user_id, document_id, 'hash_calculation',
            {
                'filename': filename,
                'algorithms': ['SHA256', 'SHA1', 'MD5'],
                'file_size': file_size
            },
            'success'
        )
        
        return {
            'hash_id': hash_id,
            'sha256': sha256_hash,
            'sha1': sha1_hash,
            'md5': md5_hash,
            'file_size': file_size,
            'algorithms_used': ['SHA256', 'SHA1', 'MD5']
        }
    
    def verify_document_integrity(self, file_content: bytes, expected_sha256: str) -> Dict[str, Any]:
        """Verify document integrity against expected hash"""
        calculated_hash = hashlib.sha256(file_content).hexdigest()
        
        return {
            'integrity_verified': calculated_hash == expected_sha256,
            'calculated_hash': calculated_hash,
            'expected_hash': expected_sha256,
            'algorithm': 'SHA256'
        }
    
    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        """Generate RSA key pair for digital signatures"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    def sign_document(self, document_hash: str, private_key_pem: bytes, 
                     signer_identity: str = None) -> Dict[str, Any]:
        """Create digital signature for document hash"""
        import uuid
        
        try:
            # Load private key
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None
            )
            
            # Sign the hash
            signature = private_key.sign(
                document_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Encode signature
            signature_b64 = base64.b64encode(signature).decode()
            
            # Get public key for verification
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            signature_id = str(uuid.uuid4())
            
            return {
                'signature_id': signature_id,
                'signature': signature_b64,
                'public_key': public_pem.decode(),
                'algorithm': 'RSA-PSS-SHA256',
                'signer_identity': signer_identity,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'Signature generation failed: {str(e)}',
                'success': False
            }
    
    def verify_signature(self, document_hash: str, signature_b64: str, 
                        public_key_pem: str) -> Dict[str, Any]:
        """Verify digital signature"""
        try:
            # Load public key
            public_key = serialization.load_pem_public_key(public_key_pem.encode())
            
            # Decode signature
            signature = base64.b64decode(signature_b64)
            
            # Verify signature
            public_key.verify(
                signature,
                document_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return {
                'signature_valid': True,
                'algorithm': 'RSA-PSS-SHA256',
                'verified_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'signature_valid': False,
                'error': str(e),
                'algorithm': 'RSA-PSS-SHA256'
            }
    
    def anchor_to_blockchain(self, document_hash: str, blockchain_network: str = 'polygon') -> Dict[str, Any]:
        """Anchor document hash to blockchain (simulated for now)"""
        import uuid
        
        anchor_id = str(uuid.uuid4())
        
        # Simulate blockchain anchoring
        # In production, this would connect to actual blockchain networks
        simulated_anchor = {
            'anchor_id': anchor_id,
            'network': blockchain_network,
            'transaction_hash': f'0x{hashlib.sha256(f"{document_hash}{anchor_id}".encode()).hexdigest()}',
            'block_number': 12345678,  # Simulated
            'gas_used': 21000,
            'transaction_fee': 0.001,
            'confirmation_status': 'confirmed',
            'anchor_timestamp': datetime.utcnow().isoformat()
        }
        
        # In production, replace with actual blockchain integration:
        # - Web3.py for Ethereum/Polygon
        # - Bitcoin RPC for Bitcoin
        # - IPFS for distributed storage
        
        return simulated_anchor
    
    def create_merkle_proof(self, document_hashes: List[str]) -> Dict[str, Any]:
        """Create Merkle tree proof for document set"""
        if not document_hashes:
            return {'error': 'No hashes provided'}
        
        # Build Merkle tree
        tree_levels = [document_hashes]
        
        while len(tree_levels[-1]) > 1:
            current_level = tree_levels[-1]
            next_level = []
            
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Hash the pair
                combined = left + right
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent_hash)
            
            tree_levels.append(next_level)
        
        merkle_root = tree_levels[-1][0]
        
        return {
            'merkle_root': merkle_root,
            'tree_depth': len(tree_levels) - 1,
            'leaf_count': len(document_hashes),
            'tree_levels': tree_levels
        }
    
    def validate_cryptographic_integrity(self, document_id: str, user_id: str) -> Dict[str, Any]:
        """Comprehensive cryptographic validation for a document"""
        try:
            # Get document hash record
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM document_hashes 
                    WHERE document_id = ? AND user_id = ?
                ''', (document_id, user_id))
                
                hash_record = cursor.fetchone()
                
                if not hash_record:
                    return {
                        'validated': False,
                        'error': 'Document hash record not found',
                        'score': 0.0
                    }
                
                # Get signatures
                cursor.execute('''
                    SELECT * FROM digital_signatures 
                    WHERE document_hash_id = ?
                ''', (hash_record['id'],))
                
                signatures = cursor.fetchall()
                
                # Get blockchain anchors
                cursor.execute('''
                    SELECT * FROM blockchain_anchors 
                    WHERE document_hash_id = ?
                ''', (hash_record['id'],))
                
                anchors = cursor.fetchall()
            
            # Calculate validation score
            score = 0.5  # Base score for having hash
            
            if signatures:
                score += 0.3  # Bonus for digital signatures
            
            if anchors:
                score += 0.2  # Bonus for blockchain anchoring
            
            validation_result = {
                'validated': True,
                'score': min(1.0, score),
                'hash_algorithms': ['SHA256', 'SHA1', 'MD5'],
                'signatures_count': len(signatures),
                'blockchain_anchors': len(anchors),
                'hash_record': {
                    'sha256': hash_record['sha256_hash'],
                    'file_size': hash_record['file_size'],
                    'created_at': hash_record['created_at']
                }
            }
            
            # Log validation
            self._log_crypto_operation(
                user_id, document_id, 'integrity_validation',
                validation_result, 'success'
            )
            
            return validation_result
            
        except Exception as e:
            error_result = {
                'validated': False,
                'error': str(e),
                'score': 0.0
            }
            
            self._log_crypto_operation(
                user_id, document_id, 'integrity_validation',
                error_result, 'error', str(e)
            )
            
            return error_result
    
    def get_document_crypto_history(self, document_id: str, user_id: str) -> Dict[str, Any]:
        """Get complete cryptographic history for a document"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get hash record
            cursor.execute('''
                SELECT * FROM document_hashes 
                WHERE document_id = ? AND user_id = ?
            ''', (document_id, user_id))
            
            hash_record = cursor.fetchone()
            
            if not hash_record:
                return {'error': 'Document not found'}
            
            # Get signatures
            cursor.execute('''
                SELECT * FROM digital_signatures 
                WHERE document_hash_id = ?
            ''', (hash_record['id'],))
            
            signatures = [dict(row) for row in cursor.fetchall()]
            
            # Get blockchain anchors
            cursor.execute('''
                SELECT * FROM blockchain_anchors 
                WHERE document_hash_id = ?
            ''', (hash_record['id'],))
            
            anchors = [dict(row) for row in cursor.fetchall()]
            
            # Get audit log
            cursor.execute('''
                SELECT * FROM crypto_audit_log 
                WHERE document_id = ? AND user_id = ?
                ORDER BY timestamp DESC
            ''', (document_id, user_id))
            
            audit_logs = [dict(row) for row in cursor.fetchall()]
        
        return {
            'document_id': document_id,
            'hash_record': dict(hash_record),
            'signatures': signatures,
            'blockchain_anchors': anchors,
            'audit_trail': audit_logs
        }
    
    def _log_crypto_operation(self, user_id: str, document_id: str, operation_type: str,
                             details: Dict[str, Any], status: str, error_message: str = None):
        """Log cryptographic operation to audit trail"""
        import uuid
        
        log_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO crypto_audit_log (
                    id, user_id, document_id, operation_type, 
                    operation_details, result_status, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (log_id, user_id, document_id, operation_type,
                  json.dumps(details), status, error_message))
    
    def get_crypto_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get cryptographic service statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            where_clause = 'WHERE user_id = ?' if user_id else ''
            params = (user_id,) if user_id else ()
            
            # Document hashes count
            cursor.execute(f'SELECT COUNT(*) FROM document_hashes {where_clause}', params)
            hash_count = cursor.fetchone()[0]
            
            # Signatures count
            cursor.execute(f'''
                SELECT COUNT(*) FROM digital_signatures ds
                JOIN document_hashes dh ON ds.document_hash_id = dh.id
                {where_clause}
            ''', params)
            signature_count = cursor.fetchone()[0]
            
            # Blockchain anchors count
            cursor.execute(f'''
                SELECT COUNT(*) FROM blockchain_anchors ba
                JOIN document_hashes dh ON ba.document_hash_id = dh.id
                {where_clause}
            ''', params)
            anchor_count = cursor.fetchone()[0]
            
            # Recent operations
            cursor.execute(f'''
                SELECT operation_type, COUNT(*) 
                FROM crypto_audit_log 
                {where_clause}
                GROUP BY operation_type
            ''', params)
            
            operations = dict(cursor.fetchall())
        
        return {
            'document_hashes': hash_count,
            'digital_signatures': signature_count,
            'blockchain_anchors': anchor_count,
            'operations_by_type': operations,
            'user_filter': user_id is not None
        }

# Global service instance
crypto_service = CryptographicService()
