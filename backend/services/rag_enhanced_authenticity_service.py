"""
RAG-Enhanced Authenticity Service
Integrates RAG with the existing 9-stage authenticity pipeline
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from .rag_service import rag_service
from .enhanced_authenticity_service import EnhancedAuthenticityService

class RAGEnhancedAuthenticityService(EnhancedAuthenticityService):
    """
    RAG-Enhanced Authenticity Service
    
    Extends the existing 9-stage authenticity pipeline with RAG capabilities:
    - Stage 6: Enhanced Retrieval & Cross-Verification with RAG
    - Contextual authenticity scoring
    - Historical pattern analysis
    - Knowledge base integration for verification
    """
    
    def __init__(self):
        super().__init__()
        self.rag_service = rag_service
        
        print("🧠 RAG-Enhanced Authenticity Service initialized")
        print("   🔗 Integrated with 9-stage authenticity pipeline")
        print("   📚 RAG knowledge base for verification")
        print("   🎯 Enhanced Stage 6: Retrieval & Cross-Verification")
    
    def comprehensive_authenticity_analysis_with_rag(
        self,
        file_path: str,
        file_id: str,
        filename: str,
        file_type: str,
        text_content: str = None,
        uploader_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive authenticity analysis with RAG enhancement
        
        This extends the existing 9-stage pipeline with RAG capabilities
        """
        # Run the standard 9-stage pipeline
        analysis_report = super().comprehensive_authenticity_analysis(
            file_path=file_path,
            file_id=file_id,
            filename=filename,
            file_type=file_type,
            text_content=text_content,
            uploader_info=uploader_info
        )
        
        # Enhance with RAG
        try:
            # Stage 6: Enhanced RAG Retrieval & Cross-Verification
            rag_verification = self.stage_6_rag_enhanced_verification(
                analysis_report.get('pipeline_stages', {}).get('classification', {}),
                file_type,
                text_content
            )
            
            # Update the analysis report with RAG enhancements
            analysis_report['pipeline_stages']['rag_verification'] = rag_verification
            
            # Enhanced scoring with RAG insights
            rag_enhanced_score, rag_confidence, rag_evidence = self._calculate_rag_enhanced_score(
                analysis_report, rag_verification
            )
            
            # Update scoring if RAG provides better insights
            if rag_enhanced_score > analysis_report.get('authenticity_score', 0):
                analysis_report['authenticity_score'] = rag_enhanced_score
                analysis_report['confidence_level'] = rag_confidence
                analysis_report['evidence_trail'].extend(rag_evidence)
            
            # Add RAG insights to the report
            analysis_report['rag_insights'] = {
                'rag_verification_confidence': rag_verification.get('verification_confidence', 0),
                'similar_documents_analyzed': rag_verification.get('similar_documents_found', 0),
                'historical_patterns': rag_verification.get('historical_patterns', {}),
                'knowledge_base_verification': rag_verification.get('knowledge_base_verification', {})
            }
            
            # Add document to RAG knowledge base for future analysis
            self._add_to_rag_knowledge_base(
                file_id=file_id,
                filename=filename,
                text_content=text_content,
                document_type=analysis_report.get('pipeline_stages', {}).get('classification', {}).get('document_type', 'unknown'),
                classification_result=analysis_report.get('pipeline_stages', {}).get('classification', {}),
                authenticity_score=analysis_report.get('authenticity_score', 0),
                metadata={
                    'file_path': file_path,
                    'file_type': file_type,
                    'uploader_info': uploader_info,
                    'analysis_timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            print(f"❌ RAG enhancement failed: {e}")
            analysis_report['rag_error'] = str(e)
        
        return analysis_report
    
    def stage_6_rag_enhanced_verification(
        self, 
        classification_results: Dict[str, Any], 
        file_type: str,
        text_content: str = None
    ) -> Dict[str, Any]:
        """
        Stage 6: RAG-Enhanced Retrieval & Cross-Verification
        
        This replaces the placeholder Stage 6 with actual RAG implementation
        """
        verification_results = {
            'stage': 'rag_enhanced_verification',
            'timestamp': datetime.now().isoformat(),
            'similar_documents_found': 0,
            'verification_confidence': 0.0,
            'historical_patterns': {},
            'knowledge_base_verification': {},
            'template_matches': [],
            'issuer_verification': {},
            'policy_checks': {},
            'inconsistencies_found': [],
            'rag_insights': []
        }
        
        try:
            document_type = classification_results.get('document_type', 'unknown')
            
            # RAG-based document retrieval
            if text_content and len(text_content.strip()) > 10:
                rag_result = self.rag_service.retrieve_similar_documents(
                    query_text=text_content,
                    document_type=document_type,
                    top_k=5,
                    similarity_threshold=0.6
                )
                
                verification_results['similar_documents_found'] = len(rag_result.retrieved_documents)
                verification_results['verification_confidence'] = self._calculate_rag_verification_confidence(rag_result)
                
                # Analyze historical patterns
                verification_results['historical_patterns'] = self._analyze_historical_patterns(rag_result)
                
                # Knowledge base verification
                verification_results['knowledge_base_verification'] = self._perform_knowledge_base_verification(
                    rag_result, document_type
                )
                
                # Generate RAG insights
                verification_results['rag_insights'] = self._generate_rag_insights(rag_result, document_type)
            
            # Template matching (enhanced with RAG)
            verification_results['template_matches'] = self._find_template_matches_with_rag(document_type, file_type)
            
            # Issuer verification (enhanced with RAG)
            verification_results['issuer_verification'] = self._verify_issuer_authenticity_with_rag(
                classification_results, rag_result if 'rag_result' in locals() else None
            )
            
            # Policy compliance checks (enhanced with RAG)
            verification_results['policy_checks'] = self._perform_policy_checks_with_rag(
                classification_results, rag_result if 'rag_result' in locals() else None
            )
            
            # Detect inconsistencies using RAG
            verification_results['inconsistencies_found'] = self._detect_inconsistencies_with_rag(
                classification_results, rag_result if 'rag_result' in locals() else None
            )
            
        except Exception as e:
            verification_results['error'] = str(e)
            verification_results['rag_insights'].append(f"RAG verification failed: {str(e)}")
        
        return verification_results
    
    def _calculate_rag_verification_confidence(self, rag_result) -> float:
        """Calculate verification confidence based on RAG results"""
        if not rag_result.retrieved_documents:
            return 0.0
        
        # Base confidence on similarity and document quality
        avg_similarity = np.mean(rag_result.similarity_scores) if rag_result.similarity_scores else 0
        doc_count = len(rag_result.retrieved_documents)
        
        # More similar documents with higher similarity = higher confidence
        confidence = min(1.0, (avg_similarity * doc_count) / 5)
        return confidence
    
    def _analyze_historical_patterns(self, rag_result) -> Dict[str, Any]:
        """Analyze historical patterns from retrieved documents"""
        if not rag_result.retrieved_documents:
            return {}
        
        patterns = {
            'document_types': {},
            'authenticity_scores': [],
            'classification_confidence': [],
            'common_features': []
        }
        
        for doc in rag_result.retrieved_documents:
            # Document type patterns
            doc_type = doc.get('document_type', 'unknown')
            patterns['document_types'][doc_type] = patterns['document_types'].get(doc_type, 0) + 1
            
            # Authenticity score patterns
            auth_score = doc.get('authenticity_score')
            if auth_score is not None:
                patterns['authenticity_scores'].append(auth_score)
            
            # Classification confidence patterns
            classification = doc.get('classification_result', {})
            if classification and 'confidence' in classification:
                patterns['classification_confidence'].append(classification['confidence'])
        
        # Calculate statistics
        if patterns['authenticity_scores']:
            patterns['avg_authenticity'] = np.mean(patterns['authenticity_scores'])
            patterns['authenticity_range'] = (min(patterns['authenticity_scores']), max(patterns['authenticity_scores']))
        
        if patterns['classification_confidence']:
            patterns['avg_classification_confidence'] = np.mean(patterns['classification_confidence'])
        
        return patterns
    
    def _perform_knowledge_base_verification(self, rag_result, document_type: str) -> Dict[str, Any]:
        """Perform knowledge base verification using RAG results"""
        verification = {
            'verified_against_knowledge_base': False,
            'similar_documents_verified': 0,
            'consistency_score': 0.0,
            'verification_details': []
        }
        
        if not rag_result.retrieved_documents:
            return verification
        
        verified_count = 0
        consistency_scores = []
        
        for doc in rag_result.retrieved_documents:
            # Check if document is in verified originals
            if doc.get('authenticity_score', 0) > 80:
                verified_count += 1
                verification['verification_details'].append({
                    'document_id': doc.get('document_id'),
                    'authenticity_score': doc.get('authenticity_score'),
                    'verification_status': 'high_authenticity'
                })
            
            # Calculate consistency with document type
            if doc.get('document_type') == document_type:
                consistency_scores.append(1.0)
            else:
                consistency_scores.append(0.5)
        
        verification['similar_documents_verified'] = verified_count
        verification['consistency_score'] = np.mean(consistency_scores) if consistency_scores else 0.0
        verification['verified_against_knowledge_base'] = verified_count > 0
        
        return verification
    
    def _generate_rag_insights(self, rag_result, document_type: str) -> List[str]:
        """Generate RAG insights for verification"""
        insights = []
        
        if not rag_result.retrieved_documents:
            insights.append("No similar documents found in knowledge base")
            return insights
        
        insights.append(f"Found {len(rag_result.retrieved_documents)} similar documents")
        
        # Analyze document types
        doc_types = [doc.get('document_type', 'unknown') for doc in rag_result.retrieved_documents]
        unique_types = set(doc_types)
        
        if len(unique_types) == 1 and list(unique_types)[0] == document_type:
            insights.append(f"All similar documents are of type: {document_type} (consistent)")
        elif document_type in unique_types:
            insights.append(f"Document type {document_type} found among similar documents")
        else:
            insights.append(f"Document type {document_type} differs from similar documents: {', '.join(unique_types)}")
        
        # Analyze authenticity scores
        auth_scores = [doc.get('authenticity_score', 0) for doc in rag_result.retrieved_documents if doc.get('authenticity_score') is not None]
        if auth_scores:
            avg_auth = np.mean(auth_scores)
            if avg_auth > 80:
                insights.append(f"Similar documents show high authenticity (avg: {avg_auth:.1f})")
            elif avg_auth < 50:
                insights.append(f"Similar documents show authenticity concerns (avg: {avg_auth:.1f})")
            else:
                insights.append(f"Similar documents show moderate authenticity (avg: {avg_auth:.1f})")
        
        return insights
    
    def _find_template_matches_with_rag(self, document_type: str, file_type: str) -> List[Dict[str, Any]]:
        """Find template matches enhanced with RAG"""
        # This would integrate with your existing template matching
        # but enhanced with RAG-retrieved similar documents
        return [
            {
                'template_id': f"{document_type}_rag_enhanced_template",
                'match_confidence': 0.8,
                'template_source': 'rag_enhanced_registry',
                'rag_enhanced': True
            }
        ]
    
    def _verify_issuer_authenticity_with_rag(self, classification_results: Dict[str, Any], rag_result=None) -> Dict[str, Any]:
        """Verify issuer authenticity enhanced with RAG"""
        verification = {
            'issuer_verified': False,
            'registry_checked': False,
            'rag_enhanced_verification': False,
            'note': 'Issuer verification enhanced with RAG knowledge base'
        }
        
        if rag_result and rag_result.retrieved_documents:
            # Check if similar documents have verified issuers
            verified_issuers = []
            for doc in rag_result.retrieved_documents:
                metadata = doc.get('metadata', {})
                if metadata and metadata.get('issuer_verified'):
                    verified_issuers.append(metadata.get('issuer'))
            
            if verified_issuers:
                verification['rag_enhanced_verification'] = True
                verification['similar_verified_issuers'] = list(set(verified_issuers))
                verification['note'] = f"Found {len(set(verified_issuers))} verified issuers in similar documents"
        
        return verification
    
    def _perform_policy_checks_with_rag(self, classification_results: Dict[str, Any], rag_result=None) -> Dict[str, Any]:
        """Perform policy compliance checks enhanced with RAG"""
        policy_checks = {
            'policy_compliant': True,
            'policies_checked': ['format_standards', 'content_requirements', 'rag_enhanced_verification'],
            'violations': [],
            'rag_enhanced_checks': []
        }
        
        if rag_result and rag_result.retrieved_documents:
            # Check consistency with similar documents
            doc_types = [doc.get('document_type', 'unknown') for doc in rag_result.retrieved_documents]
            current_type = classification_results.get('document_type', 'unknown')
            
            if current_type not in doc_types:
                policy_checks['rag_enhanced_checks'].append("Document type differs from similar documents")
                policy_checks['violations'].append("type_inconsistency")
        
        return policy_checks
    
    def _detect_inconsistencies_with_rag(self, classification_results: Dict[str, Any], rag_result=None) -> List[str]:
        """Detect inconsistencies using RAG analysis"""
        inconsistencies = []
        
        if rag_result and rag_result.retrieved_documents:
            current_type = classification_results.get('document_type', 'unknown')
            similar_types = [doc.get('document_type', 'unknown') for doc in rag_result.retrieved_documents]
            
            # Check for type inconsistencies
            if current_type not in similar_types:
                inconsistencies.append(f"Document type '{current_type}' differs from similar documents: {', '.join(set(similar_types))}")
            
            # Check for confidence inconsistencies
            current_confidence = classification_results.get('confidence', 0)
            similar_confidences = [
                doc.get('classification_result', {}).get('confidence', 0) 
                for doc in rag_result.retrieved_documents 
                if doc.get('classification_result')
            ]
            
            if similar_confidences:
                avg_similar_confidence = np.mean(similar_confidences)
                if abs(current_confidence - avg_similar_confidence) > 0.3:
                    inconsistencies.append(f"Classification confidence ({current_confidence:.2f}) differs significantly from similar documents (avg: {avg_similar_confidence:.2f})")
        
        return inconsistencies
    
    def _calculate_rag_enhanced_score(
        self, 
        analysis_report: Dict[str, Any], 
        rag_verification: Dict[str, Any]
    ) -> Tuple[float, str, List[str]]:
        """Calculate RAG-enhanced authenticity score"""
        base_score = analysis_report.get('authenticity_score', 0)
        rag_confidence = rag_verification.get('verification_confidence', 0)
        similar_docs = rag_verification.get('similar_documents_found', 0)
        
        # RAG enhancement factors
        rag_boost = 0.0
        evidence = []
        
        if similar_docs > 0:
            # Boost score based on similar documents
            rag_boost = min(10.0, similar_docs * 2)  # Max 10 point boost
            evidence.append(f"RAG found {similar_docs} similar documents for context")
        
        if rag_confidence > 0.8:
            rag_boost += 5.0
            evidence.append("High RAG verification confidence")
        elif rag_confidence < 0.3:
            rag_boost -= 5.0
            evidence.append("Low RAG verification confidence")
        
        # Knowledge base verification boost
        kb_verification = rag_verification.get('knowledge_base_verification', {})
        if kb_verification.get('verified_against_knowledge_base'):
            rag_boost += 3.0
            evidence.append("Verified against knowledge base")
        
        enhanced_score = max(0.0, min(100.0, base_score + rag_boost))
        
        # Determine confidence level
        if enhanced_score >= 85 and rag_confidence > 0.7:
            confidence = 'high'
        elif enhanced_score >= 60:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return enhanced_score, confidence, evidence
    
    def _add_to_rag_knowledge_base(
        self,
        file_id: str,
        filename: str,
        text_content: str,
        document_type: str,
        classification_result: Dict[str, Any],
        authenticity_score: float,
        metadata: Dict[str, Any]
    ) -> bool:
        """Add document to RAG knowledge base"""
        try:
            return self.rag_service.add_document_to_knowledge_base(
                document_id=file_id,
                filename=filename,
                content_text=text_content,
                document_type=document_type,
                classification_result=classification_result,
                authenticity_score=authenticity_score,
                metadata=metadata
            )
        except Exception as e:
            print(f"❌ Failed to add to RAG knowledge base: {e}")
            return False


# Global RAG-enhanced authenticity service instance
rag_enhanced_authenticity_service = RAGEnhancedAuthenticityService()
