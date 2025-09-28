import os
import uuid
import json
import mimetypes
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
from ..config.config import Config

def get_welcome_message():
    return "Welcome to the Flask API!"

def get_bert_label_name(category_id):
    """Convert BERT numeric category ID to readable name"""
    try:
        label_map_path = os.path.join(os.path.dirname(__file__), '../../BERT/models/label_map.json')
        if os.path.exists(label_map_path):
            with open(label_map_path, 'r') as f:
                label_data = json.load(f)
                label_map = label_data.get('label_map', label_data)
                return label_map.get(str(category_id), f'category_{category_id}')
        return f'category_{category_id}'
    except Exception:
        return f'category_{category_id}'

def process_upload(file):
    """Process an uploaded file and store it securely"""
    if file:
        # Generate a unique filename to prevent collisions
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{os.path.splitext(original_filename)[0]}_{timestamp}_{unique_id}{os.path.splitext(original_filename)[1]}"
        
        # Save the file
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Return file information
        return {
            'file_id': unique_id,
            'filename': original_filename,
            'status': 'success',
            'mime_type': file.content_type
        }
    return None

def analyze_document(file_id, analysis_type, user_id=None):
    """Analyze a document using real ML models"""
    # Find the file in the uploads directory
    for filename in os.listdir(Config.UPLOAD_FOLDER):
        if file_id in filename:
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            
            # Common analysis results
            base_result = {
                'file_id': file_id,
                'timestamp': datetime.now().isoformat(),
                'filename': filename,
                'analysis_type': analysis_type
            }
            
            # Determine file type
            file_ext = os.path.splitext(filename)[1].lower()
            is_image = file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
            is_pdf = file_ext == '.pdf'
            
            # Initialize ML results
            ml_classification = None
            extracted_text = None
            
            try:
                if is_image:
                    # Use ViT for image classification
                    try:
                        from .vit_classification_service import classify_image
                        with open(file_path, 'rb') as f:
                            image_bytes = f.read()
                        vit_result = classify_image(image_bytes)
                        if vit_result.get('success'):
                            ml_classification = {
                                'category': vit_result['top_prediction']['category'],
                                'confidence': vit_result['top_prediction']['confidence'],
                                'method': 'ViT (Vision Transformer)',
                                'all_predictions': vit_result.get('all_predictions', [])
                            }
                    except Exception as vit_error:
                        print(f"ViT classification failed: {vit_error}")
                
                # Extract text for BERT analysis (works for PDFs and images via OCR)
                try:
                    from .parsing_service import ParsingService
                    parsing_service = ParsingService()
                    # Get file mime type
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if not mime_type:
                        if is_image:
                            mime_type = 'image/png'
                        elif is_pdf:
                            mime_type = 'application/pdf'
                        else:
                            mime_type = 'application/octet-stream'
                    
                    parse_result = parsing_service.parse_file(file_path, filename, mime_type)
                    if parse_result and parse_result.get('raw_text'):
                        extracted_text = parse_result.get('raw_text', '')
                        
                        # Use BERT for text classification if we have text
                        if extracted_text and len(extracted_text.strip()) > 10:
                            try:
                                from .bert_classification_service import classify_document_bert
                                bert_result = classify_document_bert(extracted_text)
                                if bert_result and 'prediction' in bert_result:
                                    # Map BERT subcategories to main categories
                                    bert_category_name = bert_result['prediction']
                                    bert_confidence = bert_result['confidence']
                                    
                                    # Simple mapping of BERT predictions to main categories
                                    category_mapping = {
                                        # Current BERT model outputs (5 categories)
                                        'Financial_Insurance Document': 'insurance',
                                        'Educational Document': 'education', 
                                        'Legal Document': 'legal',
                                        'Employment Document': 'resume',
                                        'Resume': 'resume',
                                        
                                        # Additional mappings for potential BERT outputs
                                        'education': 'education', 'insurance': 'insurance', 'legal': 'legal', 'resume': 'resume',
                                        'academic_journals': 'education', 'attendance_logs': 'education', 'certificates': 'education',
                                        'degree_certificates': 'education', 'diplomas': 'education', 'enrollment_forms': 'education',
                                        'exam_results': 'education', 'grade_reports': 'education', 'student_records': 'education',
                                        'transcripts': 'education', 'university_documents': 'education', 'transcript_verification': 'education',
                                        
                                        # Insurance related  
                                        'auto_insurance': 'insurance', 'benefit_statements': 'insurance', 'claim_forms': 'insurance',
                                        'claim_verification': 'insurance', 'health_insurance': 'insurance', 'insurance_cards': 'insurance',
                                        'insurance_claims': 'insurance', 'insurance_documents': 'insurance', 'insurance_policies': 'insurance',
                                        'medical_records': 'insurance', 'policy_documents': 'insurance',
                                        
                                        # Legal related
                                        'audit_reports': 'legal', 'bid_documents': 'legal', 'consent_forms': 'legal', 'contracts': 'legal',
                                        'court_documents': 'legal', 'legal_briefs': 'legal', 'legal_opinions': 'legal', 'legal_documents': 'legal',
                                        'licensing_documents': 'legal', 'notarized_documents': 'legal', 'patent_documents': 'legal',
                                        'property_deeds': 'legal', 'regulatory_filings': 'legal', 'tax_documents': 'legal', 'wills': 'legal',
                                        'knowledge_base': 'legal',
                                        
                                        # Resume related
                                        'employment_records': 'resume', 'job_applications': 'resume', 'reference_letters': 'resume',
                                        'resumes': 'resume', 'work_experience': 'resume', 'cv': 'resume', 'portfolio': 'resume'
                                    }
                                    
                                    # Map to main category or use 'unknown' if not found
                                    main_category = category_mapping.get(bert_category_name, 'unknown')
                                    
                                    if not ml_classification:  # Use BERT if no ViT result
                                        ml_classification = {
                                            'category': main_category,
                                            'confidence': bert_confidence,
                                            'method': 'BERT (Text Classification)',
                                            'subcategory': bert_category_name,
                                            'predicted_id': bert_result.get('predicted_id', 0)
                                        }
                                    else:  # Combine ViT and BERT results
                                        ml_classification['text_analysis'] = {
                                            'category': main_category,
                                            'confidence': bert_confidence,
                                            'method': 'BERT (Text Classification)',
                                            'subcategory': bert_category_name
                                        }
                            except Exception as bert_error:
                                print(f"BERT classification failed: {bert_error}")
                except Exception as parse_error:
                    print(f"Text extraction failed: {parse_error}")
            
            except Exception as ml_error:
                print(f"ML analysis failed: {ml_error}")
                ml_classification = {
                    'category': 'unknown',
                    'confidence': 0.0,
                    'method': 'fallback',
                    'error': str(ml_error)
                }
            
            # Always route through comprehensive 9-stage pipeline first
            comprehensive_result = None
            try:
                from .enhanced_authenticity_service import EnhancedAuthenticityService
                authenticity_service = EnhancedAuthenticityService()

                comprehensive_result = authenticity_service.comprehensive_authenticity_analysis(
                    file_path=file_path,
                    file_id=file_id,
                    filename=filename,
                    file_type=file_ext,
                    text_content=extracted_text,
                    uploader_info=None
                )
            except Exception as e:
                print(f"Enhanced authenticity pipeline failed: {e}")
                comprehensive_result = None

            # Build results based on analysis type
            if analysis_type == 'authenticity':
                # Use enhanced pipeline result if available, otherwise fallback
                if comprehensive_result:
                    confidence = ml_classification['confidence'] if ml_classification else 0.5
                    category = ml_classification['category'] if ml_classification else 'unknown'

                    result = {
                        **base_result,
                        'authenticity_score': comprehensive_result.get('authenticity_score', 85.0) / 100.0,
                        'enhanced_authenticity': comprehensive_result,
                        'domain_classification': {
                            'category': category.title(),
                            'subcategory': ml_classification.get('subcategory', 'General').replace('_', ' ').title() if ml_classification else 'General',
                            'confidence': confidence
                        },
                        'confidence': confidence,
                        'ml_analysis': ml_classification,
                        'pipeline_stages': comprehensive_result.get('pipeline_stages', {}),
                        'risk_assessment': comprehensive_result.get('risk_assessment', {}),
                        'evidence_trail': comprehensive_result.get('evidence_trail', []),
                        'red_flags': comprehensive_result.get('red_flags', []),
                        'attestation': comprehensive_result.get('attestation', {})
                    }
                else:
                    # Fallback to simple analysis
                    confidence = ml_classification['confidence'] if ml_classification else 0.5
                    category = ml_classification['category'] if ml_classification else 'unknown'

                    result = {
                        **base_result,
                        'authenticity_score': min(0.95, confidence + 0.1),
                        'domain_classification': {
                            'category': category.title(),
                            'subcategory': ml_classification.get('subcategory', 'General').replace('_', ' ').title() if ml_classification else 'General',
                            'confidence': confidence
                        },
                        'confidence': confidence,
                        'ml_analysis': ml_classification,
                        'fallback_used': True
                    }
                
            elif analysis_type == 'content':
                # Use enhanced pipeline result with focus on content analysis
                if comprehensive_result:
                    confidence = ml_classification['confidence'] if ml_classification else 0.5
                    category = ml_classification['category'] if ml_classification else 'unknown'

                    result = {
                        **base_result,
                        'content_classification': {
                            'primary_category': category.title(),
                            'subcategory': ml_classification.get('subcategory', 'General').replace('_', ' ').title() if ml_classification else 'General',
                            'confidence': confidence
                        },
                        'ml_analysis': ml_classification,
                        'enhanced_content': comprehensive_result.get('content_analysis', {}),
                        'pipeline_stages': comprehensive_result.get('pipeline_stages', {}),
                        'entity_extraction': comprehensive_result.get('entity_analysis', {}),
                        'structure_analysis': {
                            'file_type': 'image' if is_image else 'document',
                            'text_extracted': bool(extracted_text),
                            'text_length': len(extracted_text) if extracted_text else 0
                        }
                    }
                else:
                    # Fallback content analysis
                    confidence = ml_classification['confidence'] if ml_classification else 0.5
                    category = ml_classification['category'] if ml_classification else 'unknown'

                    result = {
                        **base_result,
                        'content_classification': {
                            'primary_category': category.title(),
                            'subcategory': 'General',
                            'confidence': confidence
                        },
                        'ml_analysis': ml_classification,
                        'fallback_used': True
                    }
                
            elif analysis_type == 'comprehensive':
                # Return full comprehensive pipeline result
                if comprehensive_result:
                    confidence = ml_classification['confidence'] if ml_classification else 0.5
                    category = ml_classification['category'] if ml_classification else 'unknown'

                    result = {
                        **base_result,
                        'success': True,
                        'authenticity_score': comprehensive_result.get('authenticity_score', 85.0),
                        'enhanced_authenticity': comprehensive_result,
                        'domain_classification': {
                            'category': category.title(),
                            'subcategory': ml_classification.get('subcategory', 'General').replace('_', ' ').title() if ml_classification else 'General',
                            'confidence': confidence
                        },
                        'confidence': confidence,
                        'ml_analysis': ml_classification,
                        'pipeline_stages': comprehensive_result.get('pipeline_stages', {}),
                        'risk_assessment': comprehensive_result.get('risk_assessment', {}),
                        'evidence_trail': comprehensive_result.get('evidence_trail', []),
                        'red_flags': comprehensive_result.get('red_flags', []),
                        'attestation': comprehensive_result.get('attestation', {}),
                        'recommendations': comprehensive_result.get('recommendations', []),
                        # Extract Sprint 3 features for frontend
                        'fingerprint_analysis': comprehensive_result.get('fingerprint_analysis', {}),
                        'clone_detection': comprehensive_result.get('clone_detection', {}),
                        'integrity_analysis': comprehensive_result.get('integrity_analysis', {}),
                        'qr_attestation': comprehensive_result.get('qr_attestation', {}),
                        'bert_classification': {
                            'category': ml_classification.get('category', 'Unknown'),
                            'subcategory': ml_classification.get('subcategory', 'General'),
                            'confidence': ml_classification.get('confidence', 0.0)
                        } if ml_classification else None,
                        'vit_classification': comprehensive_result.get('vit_classification', {}),
                        'raw_text': extracted_text,
                        'file_type': file_ext,
                        'original_filename': filename
                    }
                else:
                    # Fallback comprehensive analysis
                    confidence = ml_classification['confidence'] if ml_classification else 0.5
                    category = ml_classification['category'] if ml_classification else 'unknown'

                    result = {
                        **base_result,
                        'authenticity_score': min(0.94, confidence + 0.1),
                        'domain_classification': {
                            'category': category.title(),
                            'subcategory': ml_classification.get('subcategory', 'General').replace('_', ' ').title() if ml_classification else 'General',
                            'confidence': confidence
                        },
                        'confidence': confidence,
                        'ml_analysis': ml_classification,
                        'fallback_used': True
                    }
                
            elif analysis_type == 'metadata':
                # Metadata-focused analysis with ML insights
                result = {
                    **base_result,
                    'ml_analysis': ml_classification,
                    'metadata': {
                        'file_size': f'{os.path.getsize(file_path) / (1024*1024):.1f} MB',
                        'file_type': 'image' if is_image else 'document',
                        'creation_date': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                        'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                        'extension': file_ext
                    },
                    'digital_properties': {
                        'has_digital_signature': False,
                        'encryption_status': False,
                        'password_protected': False,
                        'ml_classified': bool(ml_classification)
                    },
                    'integrity_check': {
                        'file_integrity': 'Intact',
                        'corruption_detected': False,
                        'ml_confidence': ml_classification['confidence'] if ml_classification else 0.0
                    }
                }
            else:
                return None
                
            # Add extracted text to all results
            result['raw_text'] = extracted_text
            
            return result
    
    return None
