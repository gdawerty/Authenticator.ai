import os
from werkzeug.utils import secure_filename
import time
import hashlib
from datetime import datetime

# Allowed file extensions
ALLOWED_EXT = {'txt', 'pdf', 'doc', 'docx', 'md', 'rtf'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def generate_unique_filename(filename):
    """Generate a unique filename using timestamp and hash"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(secure_filename(filename))
    unique_hash = hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:8]
    return f"{name}_{timestamp}_{unique_hash}{ext}"
