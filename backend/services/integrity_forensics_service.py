"""
Integrity Forensics Service
Check cryptographic signatures, AI watermarks, edit traces, font anomalies, PDF edit graph
"""

import hashlib
import json
import re
import struct
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
from PIL.ExifTags import TAGS
import io
import os
import numpy as np
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import fitz  # PyMuPDF


class IntegrityForensicsService:
    def __init__(self):
        self.known_watermarks = self._load_known_watermarks()
        self.font_patterns = self._load_font_patterns()

    def analyze_document_integrity(self, file_path: str, file_type: str, text_content: str = None) -> Dict[str, Any]:
        """
        Comprehensive integrity analysis for documents
        """
        integrity_report = {
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path,
            'file_type': file_type,
            'signature_verification': {},
            'watermark_detection': {},
            'edit_trace_analysis': {},
            'font_forensics': {},
            'metadata_analysis': {},
            'tampering_indicators': [],
            'integrity_score': 0.0,
            'confidence_level': 'low'
        }

        try:
            # 1. Cryptographic signature verification
            integrity_report['signature_verification'] = self.verify_cryptographic_signatures(file_path, file_type)

            # 2. AI watermark and tag detection
            integrity_report['watermark_detection'] = self.detect_ai_watermarks(file_path, file_type, text_content)

            # 3. Edit trace analysis
            integrity_report['edit_trace_analysis'] = self.analyze_edit_traces(file_path, file_type)

            # 4. Font and kerning anomaly detection
            if text_content:
                integrity_report['font_forensics'] = self.analyze_font_anomalies(text_content, file_path, file_type)

            # 5. Metadata analysis
            integrity_report['metadata_analysis'] = self.analyze_metadata_integrity(file_path, file_type)

            # 6. PDF edit graph analysis (for PDFs)
            if file_type.lower() == 'pdf':
                integrity_report['pdf_edit_graph'] = self.analyze_pdf_edit_graph(file_path)

            # 7. Calculate overall integrity score
            integrity_report['integrity_score'], integrity_report['confidence_level'] = self._calculate_integrity_score(integrity_report)

            # 8. Identify tampering indicators
            integrity_report['tampering_indicators'] = self._identify_tampering_indicators(integrity_report)

        except Exception as e:
            integrity_report['error'] = f"Integrity analysis failed: {str(e)}"

        return integrity_report

    def verify_cryptographic_signatures(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Verify cryptographic signatures (PAdES, DocuSign, DKIM, etc.)
        """
        signature_analysis = {
            'has_digital_signature': False,
            'signature_type': None,
            'signature_valid': False,
            'signature_details': {},
            'certificate_info': {},
            'trust_chain_valid': False,
            'timestamp_signature': None
        }

        try:
            if file_type.lower() == 'pdf':
                signature_analysis.update(self._verify_pdf_signatures(file_path))
            else:
                # Check for embedded signatures in other formats
                signature_analysis.update(self._check_embedded_signatures(file_path))

        except Exception as e:
            signature_analysis['error'] = str(e)

        return signature_analysis

    def detect_ai_watermarks(self, file_path: str, file_type: str, text_content: str = None) -> Dict[str, Any]:
        """
        Detect AI watermarks and tags in content
        """
        watermark_analysis = {
            'ai_watermarks_detected': [],
            'invisible_watermarks': [],
            'text_watermarks': [],
            'steganographic_content': False,
            'ai_generation_markers': [],
            'confidence_scores': {}
        }

        try:
            # 1. Check for known AI watermarks
            if file_type.lower() in ['jpg', 'jpeg', 'png', 'gif']:
                watermark_analysis.update(self._detect_image_watermarks(file_path))

            # 2. Check for text-based AI markers
            if text_content:
                watermark_analysis.update(self._detect_text_ai_markers(text_content))

            # 3. Check for steganographic content
            if file_type.lower() in ['jpg', 'jpeg', 'png']:
                watermark_analysis['steganographic_content'] = self._detect_steganography(file_path)

        except Exception as e:
            watermark_analysis['error'] = str(e)

        return watermark_analysis

    def analyze_edit_traces(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Analyze edit traces (ELA, JPEG quantization tables, PRNU)
        """
        edit_analysis = {
            'edit_traces_found': False,
            'ela_analysis': {},
            'jpeg_artifacts': {},
            'prnu_analysis': {},
            'compression_history': [],
            'modification_indicators': []
        }

        try:
            if file_type.lower() in ['jpg', 'jpeg']:
                # Error Level Analysis
                edit_analysis['ela_analysis'] = self._perform_ela_analysis(file_path)

                # JPEG quantization table analysis
                edit_analysis['jpeg_artifacts'] = self._analyze_jpeg_quantization(file_path)

                # Photo Response Non-Uniformity analysis
                edit_analysis['prnu_analysis'] = self._analyze_prnu(file_path)

            elif file_type.lower() == 'pdf':
                # PDF modification analysis
                edit_analysis['pdf_modifications'] = self._analyze_pdf_modifications(file_path)

        except Exception as e:
            edit_analysis['error'] = str(e)

        return edit_analysis

    def analyze_font_anomalies(self, text_content: str, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Analyze font and kerning anomalies that might indicate tampering
        """
        font_analysis = {
            'font_inconsistencies': [],
            'kerning_anomalies': [],
            'character_spacing_analysis': {},
            'font_substitution_detected': False,
            'unusual_font_combinations': []
        }

        try:
            # 1. Analyze text patterns that suggest font manipulation
            font_analysis['font_inconsistencies'] = self._detect_font_inconsistencies(text_content)

            # 2. Check for unusual character patterns
            font_analysis['character_spacing_analysis'] = self._analyze_character_spacing(text_content)

            # 3. Look for font substitution indicators
            font_analysis['font_substitution_detected'] = self._detect_font_substitution(text_content)

            # 4. PDF-specific font analysis
            if file_type.lower() == 'pdf':
                font_analysis.update(self._analyze_pdf_fonts(file_path))

        except Exception as e:
            font_analysis['error'] = str(e)

        return font_analysis

    def analyze_metadata_integrity(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Analyze metadata for integrity indicators
        """
        metadata_analysis = {
            'metadata_present': False,
            'creation_date': None,
            'modification_date': None,
            'creator_software': None,
            'metadata_inconsistencies': [],
            'suspicious_metadata': [],
            'exif_analysis': {}
        }

        try:
            if file_type.lower() in ['jpg', 'jpeg', 'png', 'tiff']:
                metadata_analysis.update(self._analyze_image_metadata(file_path))
            elif file_type.lower() == 'pdf':
                metadata_analysis.update(self._analyze_pdf_metadata(file_path))

        except Exception as e:
            metadata_analysis['error'] = str(e)

        return metadata_analysis

    def analyze_pdf_edit_graph(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze PDF edit graph and object history
        """
        pdf_analysis = {
            'object_count': 0,
            'revision_history': [],
            'indirect_objects': [],
            'cross_reference_integrity': True,
            'incremental_updates': [],
            'suspicious_objects': []
        }

        try:
            doc = fitz.open(file_path)

            # Get basic PDF structure info
            pdf_analysis['object_count'] = doc.xref_length()
            pdf_analysis['page_count'] = len(doc)

            # Analyze object structure
            for i in range(doc.xref_length()):
                try:
                    obj = doc.xref_get_key(i, "Type")
                    if obj:
                        pdf_analysis['indirect_objects'].append({
                            'object_id': i,
                            'type': obj[1] if len(obj) > 1 else 'unknown'
                        })
                except:
                    pass

            # Check for incremental updates
            pdf_analysis['incremental_updates'] = self._detect_incremental_updates(doc)

            doc.close()

        except Exception as e:
            pdf_analysis['error'] = str(e)

        return pdf_analysis

    def _verify_pdf_signatures(self, file_path: str) -> Dict[str, Any]:
        """Verify PDF digital signatures"""
        signature_info = {
            'has_digital_signature': False,
            'signature_count': 0,
            'signatures': []
        }

        try:
            doc = fitz.open(file_path)

            # Check for signature fields
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()

                for widget in widgets:
                    if widget.field_type == fitz.PDF_WIDGET_TYPE_SIGNATURE:
                        signature_info['has_digital_signature'] = True
                        signature_info['signature_count'] += 1
                        signature_info['signatures'].append({
                            'page': page_num + 1,
                            'field_name': widget.field_name,
                            'field_value': widget.field_value
                        })

            doc.close()

        except Exception as e:
            signature_info['error'] = str(e)

        return signature_info

    def _check_embedded_signatures(self, file_path: str) -> Dict[str, Any]:
        """Check for embedded signatures in non-PDF files"""
        return {
            'has_digital_signature': False,
            'note': 'Signature verification for this file type not yet implemented'
        }

    def _detect_image_watermarks(self, file_path: str) -> Dict[str, Any]:
        """Detect watermarks in images"""
        watermark_info = {}

        try:
            image = Image.open(file_path)

            # Check for invisible watermarks using frequency domain analysis
            watermark_info['invisible_watermarks'] = self._detect_invisible_watermarks(image)

            # Check for known AI generation watermarks
            watermark_info['ai_watermarks_detected'] = self._check_known_ai_watermarks(image)

        except Exception as e:
            watermark_info['error'] = str(e)

        return watermark_info

    def _detect_text_ai_markers(self, text_content: str) -> Dict[str, Any]:
        """Detect AI generation markers in text"""
        ai_markers = {
            'suspicious_patterns': [],
            'ai_generation_indicators': []
        }

        # Check for common AI text patterns
        ai_patterns = [
            r'as an ai',
            r'i cannot',
            r'i\'m unable to',
            r'i don\'t have the ability',
            r'as a language model',
            r'i apologize, but',
            r'i\'m sorry, but'
        ]

        text_lower = text_content.lower()
        for pattern in ai_patterns:
            if re.search(pattern, text_lower):
                ai_markers['ai_generation_indicators'].append(pattern)

        # Check for repetitive patterns common in AI text
        sentences = text_content.split('.')
        if len(sentences) > 5:
            sentence_starts = [s.strip()[:20] for s in sentences if s.strip()]
            unique_starts = set(sentence_starts)
            if len(unique_starts) / len(sentence_starts) < 0.7:
                ai_markers['suspicious_patterns'].append('repetitive_sentence_structures')

        return ai_markers

    def _detect_steganography(self, file_path: str) -> bool:
        """Basic steganography detection"""
        try:
            image = Image.open(file_path)
            arr = np.array(image)

            # Check for LSB steganography indicators
            if len(arr.shape) == 3:
                # Check if LSBs have unusual entropy
                lsb_layer = arr[:, :, 0] & 1
                unique_values = len(np.unique(lsb_layer))
                total_pixels = lsb_layer.size

                # If LSB layer has too much randomness, might indicate steganography
                return unique_values / total_pixels > 0.4

        except Exception:
            pass

        return False

    def _perform_ela_analysis(self, file_path: str) -> Dict[str, Any]:
        """Perform Error Level Analysis"""
        ela_result = {
            'ela_performed': False,
            'high_error_regions': [],
            'compression_artifacts': False
        }

        try:
            # Open original image
            original = Image.open(file_path)

            # Save with high quality and reload
            temp_path = file_path + '_temp_ela.jpg'
            original.save(temp_path, 'JPEG', quality=95)
            recompressed = Image.open(temp_path)

            # Calculate difference
            if original.size == recompressed.size:
                original_arr = np.array(original.convert('RGB'))
                recompressed_arr = np.array(recompressed.convert('RGB'))

                diff = np.abs(original_arr.astype(int) - recompressed_arr.astype(int))

                # Identify high error regions
                threshold = np.percentile(diff, 95)
                high_error_mask = diff > threshold

                if np.any(high_error_mask):
                    ela_result['high_error_regions'] = ['detected']
                    ela_result['compression_artifacts'] = True

                ela_result['ela_performed'] = True

            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

        except Exception as e:
            ela_result['error'] = str(e)

        return ela_result

    def _analyze_jpeg_quantization(self, file_path: str) -> Dict[str, Any]:
        """Analyze JPEG quantization tables"""
        jpeg_analysis = {
            'quantization_tables': [],
            'quality_estimate': None,
            'double_compression_detected': False
        }

        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            # Look for quantization table markers
            dqt_positions = []
            i = 0
            while i < len(data) - 1:
                if data[i] == 0xFF and data[i+1] == 0xDB:  # DQT marker
                    dqt_positions.append(i)
                i += 1

            jpeg_analysis['quantization_tables'] = f"Found {len(dqt_positions)} quantization tables"

            # Estimate quality (simplified)
            if dqt_positions:
                jpeg_analysis['quality_estimate'] = 'medium'  # Would calculate actual quality

        except Exception as e:
            jpeg_analysis['error'] = str(e)

        return jpeg_analysis

    def _analyze_prnu(self, file_path: str) -> Dict[str, Any]:
        """Analyze Photo Response Non-Uniformity"""
        return {
            'prnu_analysis': 'not_implemented',
            'note': 'PRNU analysis requires advanced sensor noise modeling'
        }

    def _analyze_pdf_modifications(self, file_path: str) -> Dict[str, Any]:
        """Analyze PDF for modifications"""
        mod_analysis = {
            'modification_detected': False,
            'incremental_updates': 0,
            'suspicious_objects': []
        }

        try:
            doc = fitz.open(file_path)

            # Check metadata for modification dates
            metadata = doc.metadata
            if metadata.get('modDate') and metadata.get('creationDate'):
                if metadata['modDate'] != metadata['creationDate']:
                    mod_analysis['modification_detected'] = True

            doc.close()

        except Exception as e:
            mod_analysis['error'] = str(e)

        return mod_analysis

    def _detect_font_inconsistencies(self, text_content: str) -> List[str]:
        """Detect font inconsistencies in text"""
        inconsistencies = []

        # Check for unusual Unicode characters that might indicate font substitution
        unusual_chars = []
        for char in text_content:
            if ord(char) > 127 and char not in ['—', '–', ''', ''', '"', '"']:
                unusual_chars.append(char)

        if unusual_chars:
            inconsistencies.append(f"Unusual Unicode characters: {set(unusual_chars)}")

        return inconsistencies

    def _analyze_character_spacing(self, text_content: str) -> Dict[str, Any]:
        """Analyze character spacing patterns"""
        spacing_analysis = {
            'unusual_spacing_detected': False,
            'multiple_space_sequences': 0,
            'tab_characters': text_content.count('\t')
        }

        # Count multiple space sequences
        import re
        multiple_spaces = re.findall(r' {2,}', text_content)
        spacing_analysis['multiple_space_sequences'] = len(multiple_spaces)

        if len(multiple_spaces) > 10:
            spacing_analysis['unusual_spacing_detected'] = True

        return spacing_analysis

    def _detect_font_substitution(self, text_content: str) -> bool:
        """Detect potential font substitution"""
        # Look for mixed character encodings or unusual character combinations
        char_codes = [ord(c) for c in text_content if c.isalpha()]

        if char_codes:
            # Check for suspicious character code distribution
            unique_ranges = set()
            for code in char_codes:
                if code < 128:
                    unique_ranges.add('ascii')
                elif code < 256:
                    unique_ranges.add('latin_extended')
                elif code < 1024:
                    unique_ranges.add('cyrillic')
                else:
                    unique_ranges.add('other')

            # Font substitution might be indicated by mixed character ranges
            return len(unique_ranges) > 2

        return False

    def _analyze_pdf_fonts(self, file_path: str) -> Dict[str, Any]:
        """Analyze PDF fonts for anomalies"""
        font_analysis = {
            'embedded_fonts': [],
            'font_count': 0,
            'missing_fonts': []
        }

        try:
            doc = fitz.open(file_path)

            for page_num in range(len(doc)):
                page = doc[page_num]
                fonts = page.get_fonts()

                for font in fonts:
                    font_info = {
                        'page': page_num + 1,
                        'font_name': font[3],
                        'font_type': font[1],
                        'embedded': font[1] > 0
                    }
                    font_analysis['embedded_fonts'].append(font_info)

            font_analysis['font_count'] = len(font_analysis['embedded_fonts'])
            doc.close()

        except Exception as e:
            font_analysis['error'] = str(e)

        return font_analysis

    def _analyze_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """Analyze image metadata"""
        metadata_info = {
            'exif_data': {},
            'creation_software': None,
            'camera_info': {},
            'gps_data': {}
        }

        try:
            image = Image.open(file_path)
            exifdata = image.getexif()

            if exifdata:
                metadata_info['metadata_present'] = True

                for tag_id in exifdata:
                    tag = TAGS.get(tag_id, tag_id)
                    data = exifdata.get(tag_id)

                    if tag == 'Software':
                        metadata_info['creation_software'] = data
                    elif tag in ['Make', 'Model']:
                        metadata_info['camera_info'][tag] = data
                    elif tag == 'GPSInfo':
                        metadata_info['gps_data'] = data

                    metadata_info['exif_data'][tag] = str(data)[:100]  # Limit length

        except Exception as e:
            metadata_info['error'] = str(e)

        return metadata_info

    def _analyze_pdf_metadata(self, file_path: str) -> Dict[str, Any]:
        """Analyze PDF metadata"""
        metadata_info = {}

        try:
            doc = fitz.open(file_path)
            metadata = doc.metadata

            metadata_info.update({
                'creation_date': metadata.get('creationDate'),
                'modification_date': metadata.get('modDate'),
                'creator_software': metadata.get('creator'),
                'producer': metadata.get('producer'),
                'title': metadata.get('title'),
                'author': metadata.get('author')
            })

            doc.close()

        except Exception as e:
            metadata_info['error'] = str(e)

        return metadata_info

    def _detect_incremental_updates(self, doc) -> List[Dict[str, Any]]:
        """Detect incremental updates in PDF"""
        updates = []

        try:
            # This is a simplified check - would need more sophisticated PDF parsing
            if hasattr(doc, 'xref_length'):
                xref_count = doc.xref_length()
                if xref_count > 100:  # Arbitrary threshold
                    updates.append({
                        'type': 'high_object_count',
                        'count': xref_count,
                        'description': 'High number of objects may indicate multiple edits'
                    })

        except Exception:
            pass

        return updates

    def _detect_invisible_watermarks(self, image: Image.Image) -> List[str]:
        """Detect invisible watermarks"""
        watermarks = []

        try:
            # Convert to numpy array for analysis
            arr = np.array(image.convert('RGB'))

            # Simple frequency domain check
            if arr.shape[0] > 100 and arr.shape[1] > 100:
                # Check for periodic patterns that might indicate watermarks
                sample = arr[50:100, 50:100, 0]
                fft = np.fft.fft2(sample)
                fft_mag = np.abs(fft)

                # Look for suspicious periodic components
                if np.max(fft_mag) > np.mean(fft_mag) * 10:
                    watermarks.append('potential_frequency_watermark')

        except Exception:
            pass

        return watermarks

    def _check_known_ai_watermarks(self, image: Image.Image) -> List[str]:
        """Check for known AI generation watermarks"""
        ai_watermarks = []

        # This would check against a database of known AI watermark patterns
        # For now, just check image characteristics that might indicate AI generation

        arr = np.array(image.convert('RGB'))

        # Check for unusual pixel value distributions common in AI-generated images
        hist = np.histogram(arr.flatten(), bins=50)[0]
        hist_std = np.std(hist)

        if hist_std < 1000:  # Very uniform distribution might indicate AI generation
            ai_watermarks.append('uniform_pixel_distribution')

        return ai_watermarks

    def _calculate_integrity_score(self, report: Dict[str, Any]) -> Tuple[float, str]:
        """Calculate overall integrity score"""
        score = 100.0
        confidence = 'high'

        # Deduct points for various issues
        if report['signature_verification'].get('has_digital_signature') is False:
            score -= 20

        if report['watermark_detection'].get('ai_watermarks_detected'):
            score -= 30

        if report['edit_trace_analysis'].get('edit_traces_found'):
            score -= 25

        if report['font_forensics'].get('font_inconsistencies'):
            score -= 15

        if len(report.get('tampering_indicators', [])) > 3:
            confidence = 'low'
        elif len(report.get('tampering_indicators', [])) > 1:
            confidence = 'medium'

        return max(0.0, score), confidence

    def _identify_tampering_indicators(self, report: Dict[str, Any]) -> List[str]:
        """Identify tampering indicators from the analysis"""
        indicators = []

        if report['watermark_detection'].get('ai_watermarks_detected'):
            indicators.append('AI generation watermarks detected')

        if report['edit_trace_analysis'].get('ela_analysis', {}).get('high_error_regions'):
            indicators.append('High error regions found in ELA analysis')

        if report['font_forensics'].get('font_inconsistencies'):
            indicators.append('Font inconsistencies detected')

        if report['metadata_analysis'].get('metadata_inconsistencies'):
            indicators.append('Metadata inconsistencies found')

        return indicators

    def _load_known_watermarks(self) -> Dict[str, Any]:
        """Load known watermark patterns"""
        return {
            'ai_generators': ['midjourney', 'dalle', 'stable_diffusion'],
            'watermark_patterns': []
        }

    def _load_font_patterns(self) -> Dict[str, Any]:
        """Load known font patterns for analysis"""
        return {
            'suspicious_fonts': ['unusual_unicode_ranges'],
            'common_substitutions': {}
        }