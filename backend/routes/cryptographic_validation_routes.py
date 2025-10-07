"""
Cryptographic Validation API Routes
Provides endpoints for file authenticity verification with digital signatures and blockchain anchoring
"""

from flask import Blueprint, request, jsonify
import os
import tempfile
from werkzeug.utils import secure_filename
from services.cryptographic_validation_service import CryptographicValidationService
from services.parsing_service import ParsingService

crypto_validation_routes = Blueprint('crypto_validation', __name__)
crypto_service = CryptographicValidationService()
parsing_service = ParsingService()


@crypto_validation_routes.route('/crypto-validation/verify', methods=['POST'])
def verify_file_authenticity():
    """
    Authenticity verification assistant endpoint that checks cryptographic integrity of files.
    
    Expected form data:
    - file: File to verify (required)
    - public_key: Public key file for signature verification (optional)
    - certificate: Certificate file for signature verification (optional)
    - check_blockchain: Whether to check blockchain anchors (default: true)
    
    Returns structured JSON report with:
    - file_hash: SHA-256 hash
    - signature_valid: True/False/null
    - timestamp_verified: True/False
    - blockchain_anchor: Transaction ID or null
    - provenance_score: 0–1 score
    """
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({
                "error": "File is required for verification",
                "status": "error"
            }), 400
        
        file = request.files['file']
        public_key = request.files.get('public_key')
        certificate = request.files.get('certificate')
        check_blockchain = request.form.get('check_blockchain', 'true').lower() == 'true'
        
        if file.filename == '':
            return jsonify({
                "error": "File must have a filename",
                "status": "error"
            }), 400
        
        # Save files temporarily
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save main file
            filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            
            # Save public key if provided
            public_key_path = None
            if public_key and public_key.filename:
                public_key_filename = secure_filename(public_key.filename)
                public_key_path = os.path.join(temp_dir, public_key_filename)
                public_key.save(public_key_path)
            
            # Save certificate if provided
            certificate_path = None
            if certificate and certificate.filename:
                certificate_filename = secure_filename(certificate.filename)
                certificate_path = os.path.join(temp_dir, certificate_filename)
                certificate.save(certificate_path)
            
            # Perform authenticity verification
            report = crypto_service.verify_file_authenticity(
                file_path=file_path,
                public_key_path=public_key_path,
                certificate_path=certificate_path,
                check_blockchain=check_blockchain
            )
            
            # Add API-specific metadata
            report.update({
                "api_endpoint": "/crypto-validation/verify",
                "original_filename": filename,
                "verification_method": "full_cryptographic_validation",
                "status": "success"
            })
            
            return jsonify(report), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Cryptographic validation failed: {str(e)}",
            "status": "error"
        }), 500


@crypto_validation_routes.route('/crypto-validation/hash', methods=['POST'])
def compute_file_hash():
    """
    Compute SHA-256 hash of a file.
    
    Expected form data:
    - file: File to hash
    
    Returns:
    - file_hash: SHA-256 hash
    - file_size: File size in bytes
    - algorithm: Hash algorithm used
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                "error": "File is required",
                "status": "error"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "error": "File must have a filename",
                "status": "error"
            }), 400
        
        # Save file temporarily
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            
            # Compute hash
            file_hash = crypto_service.compute_sha256_hash(file_path)
            file_size = os.path.getsize(file_path)
            
            return jsonify({
                "file_hash": file_hash,
                "filename": filename,
                "file_size": file_size,
                "algorithm": "SHA-256",
                "status": "success"
            }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Hash computation failed: {str(e)}",
            "status": "error"
        }), 500


@crypto_validation_routes.route('/crypto-validation/verify-signature', methods=['POST'])
def verify_signature_only():
    """
    Verify digital signature of a file.
    
    Expected form data:
    - file: File to verify
    - signature: Signature file (.sig)
    - public_key: Public key file (optional)
    - certificate: Certificate file (optional)
    
    Returns:
    - signature_valid: True/False
    - verification_details: Additional information
    """
    try:
        if 'file' not in request.files or 'signature' not in request.files:
            return jsonify({
                "error": "Both file and signature are required",
                "status": "error"
            }), 400
        
        file = request.files['file']
        signature_file = request.files['signature']
        public_key = request.files.get('public_key')
        certificate = request.files.get('certificate')
        
        if not public_key and not certificate:
            return jsonify({
                "error": "Either public_key or certificate is required for signature verification",
                "status": "error"
            }), 400
        
        # Save files temporarily
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save main file
            filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            
            # Save signature
            sig_filename = secure_filename(signature_file.filename)
            sig_path = os.path.join(temp_dir, sig_filename)
            signature_file.save(sig_path)
            
            # Load signature data
            signature_data = crypto_service._load_signature_file(sig_path)
            
            # Save public key or certificate
            public_key_path = None
            certificate_path = None
            
            if public_key:
                public_key_filename = secure_filename(public_key.filename)
                public_key_path = os.path.join(temp_dir, public_key_filename)
                public_key.save(public_key_path)
            
            if certificate:
                certificate_filename = secure_filename(certificate.filename)
                certificate_path = os.path.join(temp_dir, certificate_filename)
                certificate.save(certificate_path)
            
            # Verify signature
            signature_valid = crypto_service.verify_digital_signature(
                file_path, signature_data, public_key_path, certificate_path
            )
            
            return jsonify({
                "signature_valid": signature_valid,
                "filename": filename,
                "signature_filename": sig_filename,
                "verification_details": {
                    "algorithm": "RSA-PSS-SHA256",
                    "public_key_provided": public_key_path is not None,
                    "certificate_provided": certificate_path is not None
                },
                "status": "success"
            }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Signature verification failed: {str(e)}",
            "status": "error"
        }), 500


@crypto_validation_routes.route('/crypto-validation/blockchain-anchor', methods=['GET'])
def query_blockchain_anchor():
    """
    Query blockchain anchor for a file hash.
    
    Query parameters:
    - hash: SHA-256 hash to search for
    
    Returns:
    - blockchain_anchor: Transaction ID or null
    - network: Blockchain network
    - verified: Whether anchor is verified
    """
    try:
        file_hash = request.args.get('hash')
        
        if not file_hash:
            return jsonify({
                "error": "Hash parameter is required",
                "status": "error"
            }), 400
        
        # Validate hash format (64 hex characters for SHA-256)
        if len(file_hash) != 64 or not all(c in '0123456789abcdef' for c in file_hash.lower()):
            return jsonify({
                "error": "Invalid SHA-256 hash format",
                "status": "error"
            }), 400
        
        # Query blockchain anchor
        anchor_result = crypto_service.query_blockchain_anchor(file_hash)
        
        if anchor_result:
            return jsonify({
                "blockchain_anchor": anchor_result.get("transaction_id"),
                "network": anchor_result.get("network"),
                "verified": anchor_result.get("verified", False),
                "timestamp": anchor_result.get("timestamp"),
                "block_number": anchor_result.get("block_number"),
                "anchor_details": anchor_result,
                "status": "found"
            }), 200
        else:
            return jsonify({
                "blockchain_anchor": None,
                "network": None,
                "verified": False,
                "message": "No blockchain anchor found for this hash",
                "status": "not_found"
            }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Blockchain query failed: {str(e)}",
            "status": "error"
        }), 500


@crypto_validation_routes.route('/crypto-validation/register-anchor', methods=['POST'])
def register_blockchain_anchor():
    """
    Register a file hash on blockchain (mock implementation).
    
    Expected JSON data:
    - file_hash: SHA-256 hash to register
    - network: Blockchain network (default: mock_ledger)
    
    Returns:
    - transaction_id: Blockchain transaction ID
    - registration_details: Additional information
    """
    try:
        data = request.get_json()
        
        if not data or 'file_hash' not in data:
            return jsonify({
                "error": "file_hash is required in JSON body",
                "status": "error"
            }), 400
        
        file_hash = data['file_hash']
        network = data.get('network', 'mock_ledger')
        
        # Validate hash format
        if len(file_hash) != 64 or not all(c in '0123456789abcdef' for c in file_hash.lower()):
            return jsonify({
                "error": "Invalid SHA-256 hash format",
                "status": "error"
            }), 400
        
        # Register on blockchain
        registration_result = crypto_service.register_blockchain_anchor(file_hash, network)
        
        return jsonify({
            "transaction_id": registration_result["transaction_id"],
            "network": registration_result["network"],
            "block_number": registration_result.get("block_number"),
            "registration_details": registration_result,
            "status": "registered"
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Blockchain registration failed: {str(e)}",
            "status": "error"
        }), 500


@crypto_validation_routes.route('/crypto-validation/history', methods=['GET'])
def get_validation_history():
    """
    Get cryptographic validation history.
    
    Query parameters:
    - file_id (optional): Get history for specific file
    - limit (optional): Limit number of results
    """
    try:
        file_id = request.args.get('file_id')
        limit = int(request.args.get('limit', 50))
        
        history = crypto_service.get_validation_history(file_id)
        
        # Limit results
        if limit > 0:
            history = history[:limit]
        
        return jsonify({
            "validation_history": history,
            "count": len(history),
            "status": "success"
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Failed to get validation history: {str(e)}",
            "status": "error"
        }), 500


@crypto_validation_routes.route('/crypto-validation/blockchain-history', methods=['GET'])
def get_blockchain_history():
    """
    Get blockchain anchor history.
    
    Query parameters:
    - file_hash (optional): Get anchors for specific hash
    - limit (optional): Limit number of results
    """
    try:
        file_hash = request.args.get('file_hash')
        limit = int(request.args.get('limit', 50))
        
        anchors = crypto_service.get_blockchain_anchors(file_hash)
        
        # Limit results
        if limit > 0:
            anchors = anchors[:limit]
        
        return jsonify({
            "blockchain_anchors": anchors,
            "count": len(anchors),
            "status": "success"
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Failed to get blockchain history: {str(e)}",
            "status": "error"
        }), 500


@crypto_validation_routes.route('/crypto-validation/demo', methods=['GET'])
def demo_crypto_validation():
    """
    Demo endpoint showing cryptographic validation capabilities.
    """
    try:
        from datetime import datetime
        
        # Example verification report
        example_report = {
            "file_hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
            "signature_valid": True,
            "timestamp_verified": True,
            "blockchain_anchor": "tx_a1b2c3d4e5f67890_1696611234",
            "provenance_score": 0.9,
            "file_id": "unique_file_identifier",
            "filename": "important_document.pdf",
            "file_size": 2048576,
            "verification_timestamp": datetime.now().isoformat(),
            "verification_details": {
                "hash_algorithm": "SHA-256",
                "signature_present": True,
                "public_key_provided": True,
                "blockchain_checked": True,
                "blockchain_network": "mock_ledger"
            }
        }
        
        capabilities = {
            "hash_computation": ["SHA-256", "Efficient chunked processing", "Large file support"],
            "signature_verification": ["RSA-PSS", "X.509 certificates", "PEM public keys"],
            "blockchain_integration": ["Bitcoin", "Ethereum", "Mock ledger", "Custom networks"],
            "provenance_scoring": [
                "Base score: 0.1 (file exists)",
                "Valid signature: +0.4",
                "Blockchain anchor: +0.3",
                "Timestamp verified: +0.2",
                "Invalid signature: -0.1"
            ],
            "output_format": [
                "file_hash (SHA-256)",
                "signature_valid (True/False/null)",
                "timestamp_verified (True/False)",
                "blockchain_anchor (TX ID or null)",
                "provenance_score (0–1)"
            ]
        }
        
        return jsonify({
            "message": "Cryptographic Validation Service - Authenticity verification assistant",
            "example_report": example_report,
            "capabilities": capabilities,
            "endpoints": {
                "verify": "/crypto-validation/verify - Full authenticity verification",
                "hash": "/crypto-validation/hash - Compute SHA-256 hash",
                "verify_signature": "/crypto-validation/verify-signature - Signature verification only",
                "blockchain_anchor": "/crypto-validation/blockchain-anchor - Query blockchain anchor",
                "register_anchor": "/crypto-validation/register-anchor - Register blockchain anchor",
                "history": "/crypto-validation/history - Get validation history",
                "blockchain_history": "/crypto-validation/blockchain-history - Get blockchain history",
                "demo": "/crypto-validation/demo - This demo endpoint"
            },
            "status": "ready"
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Demo failed: {str(e)}",
            "status": "error"
        }), 500


@crypto_validation_routes.route('/crypto-validation/status', methods=['GET'])
def get_service_status():
    """Get cryptographic validation service status."""
    try:
        return jsonify({
            "service_status": "operational",
            "database_path": crypto_service.db_path,
            "supported_algorithms": ["SHA-256", "RSA-PSS"],
            "blockchain_networks": list(crypto_service.blockchain_apis.keys()),
            "features": [
                "File hash computation",
                "Digital signature verification",
                "Blockchain anchor querying",
                "Provenance scoring",
                "Validation history"
            ],
            "status": "ready"
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Status check failed: {str(e)}",
            "status": "error"
        }), 500
