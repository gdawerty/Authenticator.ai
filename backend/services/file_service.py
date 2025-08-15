import os
from werkzeug.utils import secure_filename
import time
from datetime import datetime

class FileService:
    def __init__(self, app):
        self.app = app
        
    def save_file(self, file):
        """Save uploaded file with a unique filename"""
        filename = self._generate_unique_filename(file.filename)
        filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return {
            'filename': filename,
            'filepath': filepath,
            'size': os.path.getsize(filepath),
            'mime_type': self._get_mime_type(filepath)
        }
        
    def _generate_unique_filename(self, original_filename):
        """Generate a unique filename based on timestamp and original name"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        secure_name = secure_filename(original_filename)
        name, ext = os.path.splitext(secure_name)
        return f"{name}_{timestamp}{ext}"
        
    def _get_mime_type(self, filepath):
        """Get MIME type of the file"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filepath)
        return mime_type or 'application/octet-stream'
