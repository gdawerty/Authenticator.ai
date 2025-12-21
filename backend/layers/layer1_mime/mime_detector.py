"""
Layer 1: MIME Detection
Analyzes file structure and format to detect the actual file type, regardless of extension.
"""

import mimetypes
import magic
import os
from typing import Dict, Any

class MIMEDetectionLayer:
    """
    Layer 1: MIME Type Detection
    Detects file types using multiple methods for accuracy
    """
    
    def __init__(self):
        self.layer_name = "MIME Detection"
        self.layer_number = 1
        
    def analyze(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Analyze file for MIME type detection
        
        Args:
            file_path: Path to the file
            filename: Original filename
            
        Returns:
            Dictionary with MIME analysis results
        """
        try:
            # Method 1: Use python-magic for accurate detection
            try:
                import magic
                mime_type = magic.from_file(file_path, mime=True)
                file_type = magic.from_file(file_path)
            except:
                # Fallback to mimetypes
                mime_type, _ = mimetypes.guess_type(filename)
                file_type = "Unknown"
            
            # Method 2: File signature analysis
            detected_type = self._detect_by_signature(file_path)
            
            # Method 3: Extension-based detection
            extension_type = self._detect_by_extension(filename)
            
            # Confidence scoring
            confidence = self._calculate_confidence(mime_type, detected_type, extension_type)
            
            return {
                "status": "completed",
                "score": confidence,
                "mime_type": mime_type,
                "detected_type": detected_type,
                "extension_type": extension_type,
                "file_type": file_type,
                "details": f"File type: {detected_type or extension_type}",
                "layer": self.layer_number,
                "layer_name": self.layer_name
            }
            
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "error": str(e),
                "layer": self.layer_number,
                "layer_name": self.layer_name
            }
    
    def _detect_by_signature(self, file_path: str) -> str:
        """Detect file type by reading file signatures"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(1024)
            
            # File signatures
            if header.startswith(b'%PDF'):
                return "PDF"
            elif header.startswith(b'\x89PNG'):
                return "PNG"
            elif header.startswith(b'\xff\xd8\xff'):
                return "JPEG"
            elif header.startswith(b'PK\x03\x04'):
                return "ZIP/Office"
            elif header.startswith(b'\xd0\xcf\x11\xe0'):
                return "MS Office"
            elif header.startswith(b'GIF8'):
                return "GIF"
            else:
                return "Unknown"
                
        except Exception:
            return "Unknown"
    
    def _detect_by_extension(self, filename: str) -> str:
        """Detect file type by extension"""
        if '.' not in filename:
            return "Unknown"
        
        ext = filename.split('.')[-1].upper()
        extension_map = {
            'PDF': 'PDF',
            'DOCX': 'DOCX',
            'DOC': 'DOC',
            'TXT': 'TEXT',
            'PNG': 'PNG',
            'JPG': 'JPEG',
            'JPEG': 'JPEG',
            'GIF': 'GIF'
        }
        
        return extension_map.get(ext, ext)
    
    def _calculate_confidence(self, mime_type: str, detected_type: str, extension_type: str) -> float:
        """Calculate confidence score based on detection consistency"""
        matches = 0
        total = 0
        
        if mime_type:
            total += 1
            if detected_type and detected_type.lower() in mime_type.lower():
                matches += 1
        
        if detected_type and detected_type != "Unknown":
            total += 1
            if extension_type and extension_type.lower() in detected_type.lower():
                matches += 1
        
        if total == 0:
            return 0.5
        
        confidence = matches / total
        return min(max(confidence, 0.5), 1.0)  # Ensure between 0.5 and 1.0
