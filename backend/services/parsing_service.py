"""
File Parsing & OCR Service
Handles PDF, Image, and DOCX file parsing with OCR capabilities
"""

import os
import json
import time
from typing import Dict, List, Optional, Tuple, Any
import re
from datetime import datetime
import hashlib

# Core libraries with error handling
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    from PIL import Image, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    ImageEnhance = None

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    fitz = None

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    Document = None

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    pytesseract = None

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    easyocr = None

try:
    # import pyzbar.pyzbar as pyzbar
    # PYZBAR_AVAILABLE = True
    PYZBAR_AVAILABLE = False
    pyzbar = None
except ImportError:
    PYZBAR_AVAILABLE = False
    pyzbar = None

class ParsingService:
    def __init__(self):
        self.supported_types = {
            'application/pdf': 'pdf',
            'image/jpeg': 'image',
            'image/jpg': 'image', 
            'image/png': 'image',
            'image/tiff': 'image',
            'image/bmp': 'image',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx'
        }
        
        # Vision tags for zero-shot classification
        self.vision_tags = [
            'document', 'text', 'handwriting', 'form', 'receipt', 'invoice',
            'certificate', 'identification', 'passport', 'license', 'contract',
            'letter', 'email', 'newspaper', 'book', 'magazine', 'poster',
            'sign', 'logo', 'chart', 'graph', 'table', 'diagram', 'map',
            'photo', 'screenshot', 'scan', 'digital', 'printed', 'typed'
        ]

    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of available OCR and vision capabilities"""
        return {
            'ocr_available': PYTESSERACT_AVAILABLE or EASYOCR_AVAILABLE,
            'pytesseract_available': PYTESSERACT_AVAILABLE,
            'easyocr_available': EASYOCR_AVAILABLE,
            'cv2_available': CV2_AVAILABLE,
            'pil_available': PIL_AVAILABLE,
            'qr_detection_available': PYZBAR_AVAILABLE,
            'vision_analysis_available': CV2_AVAILABLE and NUMPY_AVAILABLE,
            'pdf_processing_available': FITZ_AVAILABLE,
            'docx_processing_available': DOCX_AVAILABLE
        }

    def parse_file(self, file_path: str, filename: str, mime_type: str) -> Dict[str, Any]:
        """
        Main parsing function that handles different file types
        Returns structured data according to AC requirements
        """
        try:
            start_time = time.time()
            
            # Validate file type
            if mime_type not in self.supported_types:
                raise ValueError(f"Unsupported file type: {mime_type}")
            
            file_type = self.supported_types[mime_type]
            file_id = self._generate_file_id(file_path, filename)
            
            # Initialize result structure
            result = {
                'file_id': file_id,
                'filename': filename,
                'mime_type': mime_type,
                'file_type': file_type,
                'raw_text': '',
                'pages': [],
                'ocr_used': False,
                'extraction_confidence': 0.0,
                'notes': [],
                'processing_time': 0.0,
                'timestamp': datetime.utcnow().isoformat(),
                'vision': {
                    'tags': [],
                    'qr_codes': []
                }
            }
            
            # Process based on file type
            if file_type == 'pdf':
                result = self._parse_pdf(file_path, result)
            elif file_type == 'image':
                result = self._parse_image(file_path, result)
            elif file_type == 'docx':
                result = self._parse_docx(file_path, result)
            
            # Calculate processing time
            result['processing_time'] = round(time.time() - start_time, 3)
            
            # Persist to JSONL
            self._persist_to_jsonl(result)
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'filename': filename,
                'mime_type': mime_type,
                'timestamp': datetime.utcnow().isoformat()
            }

    def _parse_pdf(self, file_path: str, result: Dict) -> Dict:
        """Parse PDF files with native text extraction and OCR fallback"""
        try:
            doc = fitz.open(file_path)
            total_confidence = 0.0
            page_count = 0
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_data = {
                    'page_number': page_num + 1,
                    'blocks': [],
                    'ocr_confidence': 0.0,
                    'extraction_method': 'native'
                }
                
                # Try native text extraction first
                text_dict = page.get_text("dict")
                native_text = page.get_text().strip()
                
                # Heuristic: if native text is very short, likely scanned
                needs_ocr = len(native_text) < 50 or self._is_low_quality_text(native_text)
                
                if needs_ocr:
                    # Convert page to image for OCR
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                    img_data = pix.tobytes("png")
                    
                    # Perform OCR
                    ocr_result = self._perform_ocr(img_data, is_pdf_page=True)
                    page_data['blocks'] = ocr_result['blocks']
                    page_data['ocr_confidence'] = ocr_result['confidence']
                    page_data['extraction_method'] = 'ocr'
                    result['ocr_used'] = True
                    
                    if ocr_result['confidence'] < 0.7:
                        result['notes'].append(f"Low OCR confidence on page {page_num + 1}: {ocr_result['confidence']:.2f}")
                else:
                    # Use native text extraction
                    for block in text_dict.get("blocks", []):
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line.get("spans", []):
                                    page_data['blocks'].append({
                                        'bbox': span.get('bbox', [0, 0, 0, 0]),
                                        'text': span.get('text', ''),
                                        'confidence': 1.0  # Native extraction is highly confident
                                    })
                    page_data['ocr_confidence'] = 1.0
                
                # Extract text for this page
                page_text = ' '.join([block['text'] for block in page_data['blocks']])
                result['raw_text'] += page_text + '\n'
                
                total_confidence += page_data['ocr_confidence']
                page_count += 1
                result['pages'].append(page_data)
            
            doc.close()
            
            # Calculate overall extraction confidence
            result['extraction_confidence'] = total_confidence / page_count if page_count > 0 else 0.0
            
            return result
            
        except Exception as e:
            result['notes'].append(f"PDF parsing error: {str(e)}")
            result['extraction_confidence'] = 0.0
            return result

    def _parse_image(self, file_path: str, result: Dict) -> Dict:
        """Parse image files with OCR and vision analysis"""
        try:
            if not PIL_AVAILABLE:
                raise Exception("PIL/Pillow not available for image processing")
                
            # Load image
            image = Image.open(file_path)
            
            # Check if image should be classified rather than OCR'd
            should_classify = self._should_use_classification(image)
            
            if should_classify:
                # Mark for classification LLM processing
                result['classification_recommended'] = True
                result['raw_text'] = '[Image Classification Required - Complex visual content detected]'
                result['ocr_used'] = False
                result['extraction_confidence'] = 0.0
                result['notes'].append("Image contains complex visual content. Classification LLM recommended for proper analysis.")
                
                page_data = {
                    'page_number': 1,
                    'blocks': [{
                        'text': '[Complex Visual Content - Classification Needed]',
                        'confidence': 0.0,
                        'bbox': [0, 0, image.width, image.height]
                    }],
                    'ocr_confidence': 0.0,
                    'extraction_method': 'classification_needed'
                }
                result['pages'].append(page_data)
            else:
                # Perform OCR
                ocr_result = self._perform_ocr(file_path, is_pdf_page=False)
                
                page_data = {
                    'page_number': 1,
                    'blocks': ocr_result['blocks'],
                    'ocr_confidence': ocr_result['confidence'],
                    'extraction_method': 'ocr'
                }
                
                result['pages'].append(page_data)
                result['raw_text'] = ' '.join([block['text'] for block in ocr_result['blocks']])
                result['ocr_used'] = True
                result['extraction_confidence'] = ocr_result['confidence']
                result['classification_recommended'] = False
                
                if ocr_result['confidence'] < 0.7:
                    result['notes'].append(f"Low OCR confidence: {ocr_result['confidence']:.2f}")
            
            # Vision analysis (if available)
            if PIL_AVAILABLE:
                result['vision']['tags'] = self._analyze_image_content(image)
            if PYZBAR_AVAILABLE:
                result['vision']['qr_codes'] = self._detect_qr_codes(file_path)
            
            return result
            
        except Exception as e:
            result['notes'].append(f"Image parsing error: {str(e)}")
            result['extraction_confidence'] = 0.0
            return result

    def _parse_docx(self, file_path: str, result: Dict) -> Dict:
        """Parse DOCX files"""
        try:
            doc = Document(file_path)
            
            page_data = {
                'page_number': 1,
                'blocks': [],
                'ocr_confidence': 1.0,
                'extraction_method': 'native'
            }
            
            # Extract text from paragraphs
            for i, paragraph in enumerate(doc.paragraphs):
                if paragraph.text.strip():
                    page_data['blocks'].append({
                        'bbox': [0, i * 20, 100, (i + 1) * 20],  # Estimated positions
                        'text': paragraph.text,
                        'confidence': 1.0
                    })
                    result['raw_text'] += paragraph.text + '\n'
            
            result['pages'].append(page_data)
            result['extraction_confidence'] = 1.0
            
            return result
            
        except Exception as e:
            result['notes'].append(f"DOCX parsing error: {str(e)}")
            result['extraction_confidence'] = 0.0
            return result

    def _perform_ocr(self, image_input, is_pdf_page: bool = False) -> Dict:
        """Perform OCR on image data or file path"""
        try:
            if not PYTESSERACT_AVAILABLE and not EASYOCR_AVAILABLE:
                return {
                    'blocks': [{'text': 'OCR not available - missing dependencies', 'confidence': 0.0, 'bbox': [0, 0, 0, 0]}],
                    'confidence': 0.0
                }
                
            if not PIL_AVAILABLE:
                return {
                    'blocks': [{'text': 'Image processing not available - missing PIL', 'confidence': 0.0, 'bbox': [0, 0, 0, 0]}],
                    'confidence': 0.0
                }
            
            if is_pdf_page:
                # Image data from PDF page
                import io
                image = Image.open(io.BytesIO(image_input))
            else:
                # File path
                image = Image.open(image_input)
            
            # Enhance image for better OCR
            image = self._enhance_image_for_ocr(image)
            
            if PYTESSERACT_AVAILABLE and CV2_AVAILABLE and NUMPY_AVAILABLE:
                # Convert to OpenCV format
                cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Get detailed OCR data
                ocr_data = pytesseract.image_to_data(cv_image, output_type=pytesseract.Output.DICT)
                
                blocks = []
                confidences = []
                
                for i in range(len(ocr_data['text'])):
                    text = ocr_data['text'][i].strip()
                    conf = float(ocr_data['conf'][i])
                    
                    if text and conf > 0:
                        x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
                        
                        blocks.append({
                            'bbox': [x, y, x + w, y + h],
                            'text': text,
                            'confidence': conf / 100.0  # Normalize to 0-1
                        })
                        confidences.append(conf / 100.0)
                
                overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                
                return {
                    'blocks': blocks,
                    'confidence': overall_confidence
                }
            else:
                # Fallback to basic text extraction
                return {
                    'blocks': [{'text': 'Basic OCR - limited functionality', 'confidence': 0.5, 'bbox': [0, 0, 100, 20]}],
                    'confidence': 0.5
                }
            
        except Exception as e:
            return {
                'blocks': [],
                'confidence': 0.0,
                'error': str(e)
            }

    def _enhance_image_for_ocr(self, image) -> Any:
        """Enhance image quality for better OCR results"""
        try:
            if not PIL_AVAILABLE or not Image:
                return image
                
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Resize if too small
            width, height = image.size
            if width < 1000 or height < 1000:
                scale_factor = max(1000 / width, 1000 / height)
                new_size = (int(width * scale_factor), int(height * scale_factor))
                image = image.resize(new_size, getattr(Image, 'LANCZOS', 1))
            
            return image
            
        except Exception:
            return image

    def _analyze_image_content(self, image) -> List[str]:
        """Analyze image content for vision tags (simplified zero-shot classification)"""
        try:
            # Convert to CV2 format for analysis
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Simple heuristics for content classification
            tags = []
            
            # Check for text-heavy content
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            text_areas = cv2.findContours(cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1], 
                                        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
            
            if len(text_areas) > 10:
                tags.extend(['document', 'text'])
            
            # Check aspect ratio for document types
            height, width = cv_image.shape[:2]
            aspect_ratio = width / height
            
            if 0.7 <= aspect_ratio <= 0.8:  # Letter/A4 ratio
                tags.append('document')
            elif aspect_ratio > 1.3:
                tags.append('landscape')
            
            # Check for high contrast (typical of scanned documents)
            std_dev = np.std(gray)
            if std_dev > 60:
                tags.append('scan')
            
            return list(set(tags))  # Remove duplicates
            
        except Exception:
            return ['image']  # Fallback

    def _detect_qr_codes(self, image_path: str) -> List[Dict]:
        """Detect QR codes in images"""
        try:
            if not PYZBAR_AVAILABLE or not CV2_AVAILABLE:
                return []  # QR detection not available
                
            image = cv2.imread(image_path)
            qr_codes = []
            
            # Detect QR codes
            decoded_objects = pyzbar.decode(image)
            
            for obj in decoded_objects:
                # Get bounding box
                points = obj.polygon
                if len(points) == 4:
                    bbox = [
                        min(p.x for p in points),
                        min(p.y for p in points),
                        max(p.x for p in points),
                        max(p.y for p in points)
                    ]
                else:
                    bbox = [obj.rect.left, obj.rect.top, 
                           obj.rect.left + obj.rect.width, 
                           obj.rect.top + obj.rect.height]
                
                qr_codes.append({
                    'type': obj.type,
                    'data': obj.data.decode('utf-8'),
                    'bbox': bbox,
                    'confidence': 1.0  # QR detection is binary
                })
            
            return qr_codes
            
        except Exception:
            return []

    def _is_low_quality_text(self, text: str) -> bool:
        """Heuristic to detect low-quality native text extraction"""
        if len(text.strip()) == 0:
            return True
        
        # Check for excessive special characters (common in OCR artifacts)
        special_char_ratio = len(re.findall(r'[^\w\s]', text)) / len(text)
        if special_char_ratio > 0.3:
            return True
        
        # Check for very short "words" (potential OCR errors)
        words = text.split()
        short_words = [w for w in words if len(w) == 1 and w.isalpha()]
        if len(short_words) / len(words) > 0.5:
            return True
        
        return False

    def _should_use_classification(self, image) -> bool:
        """
        Determine if an image should be processed by classification LLM
        instead of OCR based on content analysis
        """
        try:
            if not CV2_AVAILABLE or not NUMPY_AVAILABLE:
                # Without computer vision, default to OCR
                return False
            
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 1. Detect if image has significant non-text content
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Edge detection to find complex shapes/objects
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # If high edge density, likely contains complex objects
            if edge_density > 0.15:
                return True
            
            # 2. Color analysis - complex images usually have varied colors
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
            
            # Calculate color diversity
            h_entropy = -np.sum(hist_h * np.log(hist_h + 1e-10))
            s_entropy = -np.sum(hist_s * np.log(hist_s + 1e-10))
            
            # High color entropy suggests complex visual content
            if h_entropy > 4.0 or s_entropy > 6.0:
                return True
            
            # 3. Try basic OCR to check text quality
            if PYTESSERACT_AVAILABLE:
                # Quick OCR test
                text = pytesseract.image_to_string(cv_image, config='--psm 6')
                
                # If very little readable text found, likely needs classification
                readable_chars = len(re.findall(r'[a-zA-Z0-9]', text))
                total_chars = len(text.strip())
                
                if total_chars == 0 or (readable_chars / max(total_chars, 1)) < 0.3:
                    return True
                
                # Check for very fragmented text (sign of complex image)
                words = text.split()
                if len(words) < 5 and total_chars > 20:
                    return True
            
            # 4. Check aspect ratio and size - screenshots/photos often need classification
            height, width = cv_image.shape[:2]
            aspect_ratio = width / height
            
            # Very wide or very tall images might be screenshots or photos
            if aspect_ratio > 3.0 or aspect_ratio < 0.3:
                return True
            
            return False
            
        except Exception:
            # If analysis fails, default to OCR
            return False

    def _generate_file_id(self, file_path: str, filename: str) -> str:
        """Generate unique file ID"""
        content = f"{filename}_{os.path.getsize(file_path)}_{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()

    def _persist_to_jsonl(self, result: Dict) -> None:
        """Persist parsing results to JSONL file"""
        try:
            log_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'parsing_logs')
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, 'parsing_results.jsonl')
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
                
        except Exception as e:
            print(f"Failed to persist to JSONL: {e}")

# Import required for image processing
import io

# Global service instance
parsing_service = ParsingService()
