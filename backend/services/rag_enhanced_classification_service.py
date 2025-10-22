"""
RAG-Enhanced Classification Service
Integrates RAG with existing BERT, ViT, and clone detection models
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from .rag_service import RAGService, rag_service
from .classification_service import ClassificationService
from .enhanced_clone_detection_service import EnhancedCloneDetectionService
from .ai_clone_detection_service import AICloneDetectionService

class RAGEnhancedClassificationService:
    """
    RAG-Enhanced Classification Service
    
    Integrates RAG with existing classification models:
    - BERT text classification with RAG context
    - ViT image classification with similar image retrieval
    - Enhanced clone detection with historical patterns
    - Multi-modal RAG for comprehensive analysis
    """
    
    def __init__(self):
        self.rag_service = rag_service
        self.classification_service = ClassificationService()
        self.clone_detection_service = EnhancedCloneDetectionService()
        self.ai_clone_service = AICloneDetectionService()
        
        print("🧠 RAG-Enhanced Classification Service initialized")
        print("   🔗 Integrated with BERT, ViT, and clone detection")
        print("   📚 RAG knowledge base ready")
        print("   🎯 Enhanced classification with context")
    
    def classify_document_with_rag(
        self, 
        file_path: str, 
        filename: str = None,
        document_type_hint: str = None,
        extract_embeddings: bool = True
    ) -> Dict[str, Any]:
        """
        Classify document using RAG-enhanced classification
        
        Args:
            file_path: Path to document
            filename: Document filename
            document_type_hint: Optional document type hint
            extract_embeddings: Whether to extract embeddings
        
        Returns:
            RAG-enhanced classification results
        """
        try:
            # Step 1: Standard classification
            standard_result = self.classification_service.classify_document(
                file_path, extract_embeddings=extract_embeddings
            )
            
            if standard_result.get('error'):
                return standard_result
            
            # Step 2: Extract text content for RAG
            text_content = self._extract_text_for_rag(file_path, standard_result)
            
            # Step 3: RAG enhancement
            rag_enhanced_result = self.rag_service.enhance_classification_with_rag(
                text_content=text_content,
                current_classification=standard_result.get('classification_result', {}),
                document_type=document_type_hint
            )
            
            # Step 4: Combine results
            enhanced_result = standard_result.copy()
            enhanced_result['rag_enhancement'] = rag_enhanced_result.get('rag_enhancement', {})
            enhanced_result['classification_result'] = rag_enhanced_result
            
            # Step 5: Add to knowledge base for future RAG
            self._add_to_rag_knowledge_base(
                file_path=file_path,
                filename=filename,
                text_content=text_content,
                classification_result=rag_enhanced_result,
                document_type=rag_enhanced_result.get('predicted_category', 'unknown')
            )
            
            return enhanced_result
            
        except Exception as e:
            return {
                'error': f"RAG-enhanced classification failed: {str(e)}",
                'standard_result': standard_result if 'standard_result' in locals() else None
            }
    
    def analyze_document_similarity_with_rag(
        self, 
        text_content: str, 
        file_id: str, 
        filename: str = None,
        document_type: str = None
    ) -> Dict[str, Any]:
        """
        Analyze document similarity using RAG-enhanced clone detection
        
        Args:
            text_content: Document text content
            file_id: Unique document identifier
            filename: Document filename
            document_type: Document type
        
        Returns:
            RAG-enhanced similarity analysis
        """
        try:
            # Step 1: Standard clone detection
            clone_result = self.clone_detection_service.process_document(
                text=text_content,
                file_id=file_id,
                filename=filename,
                document_type=document_type
            )
            
            # Step 2: RAG similarity analysis
            rag_similarity = self.rag_service.retrieve_similar_documents(
                query_text=text_content,
                document_type=document_type,
                top_k=5,
                similarity_threshold=0.6
            )
            
            # Step 3: Combine clone detection with RAG insights
            enhanced_result = clone_result.copy()
            enhanced_result['rag_similarity_analysis'] = {
                'similar_documents_found': len(rag_similarity.retrieved_documents),
                'average_similarity': float(np.mean(rag_similarity.similarity_scores)) if rag_similarity.similarity_scores else 0.0,
                'similar_document_types': list(set([
                    doc.get('document_type', 'unknown') 
                    for doc in rag_similarity.retrieved_documents
                ])),
                'context_insights': self._generate_similarity_insights(rag_similarity),
                'retrieval_metadata': rag_similarity.metadata
            }
            
            # Step 4: Enhanced similarity scoring
            enhanced_result['enhanced_similarity_score'] = self._calculate_enhanced_similarity_score(
                clone_result.get('similarity_score', 0.0),
                rag_similarity
            )
            
            return enhanced_result
            
        except Exception as e:
            return {
                'error': f"RAG similarity analysis failed: {str(e)}",
                'standard_result': clone_result if 'clone_result' in locals() else None
            }
    
    def comprehensive_rag_analysis(
        self, 
        file_path: str, 
        file_id: str, 
        filename: str = None,
        document_type_hint: str = None
    ) -> Dict[str, Any]:
        """
        Comprehensive RAG-enhanced analysis combining all models
        
        Args:
            file_path: Path to document
            file_id: Unique document identifier
            filename: Document filename
            document_type_hint: Optional document type hint
        
        Returns:
            Comprehensive RAG analysis results
        """
        try:
            # Step 1: RAG-enhanced classification
            classification_result = self.classify_document_with_rag(
                file_path=file_path,
                filename=filename,
                document_type_hint=document_type_hint
            )
            
            # Step 2: Extract text for similarity analysis
            text_content = self._extract_text_for_rag(file_path, classification_result)
            
            # Step 3: RAG-enhanced similarity analysis
            similarity_result = self.analyze_document_similarity_with_rag(
                text_content=text_content,
                file_id=file_id,
                filename=filename,
                document_type=classification_result.get('classification_result', {}).get('predicted_category')
            )
            
            # Step 4: RAG authenticity verification
            authenticity_verification = self.rag_service.verify_authenticity_with_rag(
                document_id=file_id,
                authenticity_score=85.0,  # Default score, would come from authenticity pipeline
                document_type=classification_result.get('classification_result', {}).get('predicted_category', 'unknown'),
                metadata={
                    'content_text': text_content,
                    'filename': filename,
                    'file_path': file_path
                }
            )
            
            # Step 5: Combine all results
            comprehensive_result = {
                'analysis_id': f"rag_analysis_{file_id}_{int(datetime.now().timestamp())}",
                'timestamp': datetime.now().isoformat(),
                'file_info': {
                    'file_id': file_id,
                    'filename': filename,
                    'file_path': file_path
                },
                'classification': classification_result,
                'similarity_analysis': similarity_result,
                'authenticity_verification': authenticity_verification,
                'rag_insights': self._generate_comprehensive_insights(
                    classification_result, similarity_result, authenticity_verification
                ),
                'recommendations': self._generate_rag_recommendations(
                    classification_result, similarity_result, authenticity_verification
                )
            }
            
            return comprehensive_result
            
        except Exception as e:
            return {
                'error': f"Comprehensive RAG analysis failed: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def _extract_text_for_rag(self, file_path: str, classification_result: Dict[str, Any]) -> str:
        """Extract text content for RAG processing"""
        try:
            # Try to get text from classification result first
            if 'text_preview' in classification_result:
                return classification_result['text_preview']
            
            # Fallback to parsing service
            from .parsing_service import parsing_service
            
            file_extension = os.path.splitext(file_path)[1].lower()
            mime_type = self._get_mime_type(file_extension)
            
            parse_result = parsing_service.parse_file(file_path, os.path.basename(file_path), mime_type)
            return parse_result.get('raw_text', '')
            
        except Exception as e:
            print(f"❌ Failed to extract text for RAG: {e}")
            return ""
    
    def _get_mime_type(self, file_extension: str) -> str:
        """Get MIME type from file extension"""
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain'
        }
        return mime_types.get(file_extension.lower(), 'application/octet-stream')
    
    def _add_to_rag_knowledge_base(
        self, 
        file_path: str, 
        filename: str, 
        text_content: str,
        classification_result: Dict[str, Any],
        document_type: str
    ) -> bool:
        """Add document to RAG knowledge base"""
        try:
            return self.rag_service.add_document_to_knowledge_base(
                document_id=f"rag_{hashlib.md5(file_path.encode()).hexdigest()[:12]}",
                filename=filename or os.path.basename(file_path),
                content_text=text_content,
                document_type=document_type,
                classification_result=classification_result,
                authenticity_score=85.0,  # Default, would come from authenticity pipeline
                metadata={
                    'file_path': file_path,
                    'analysis_timestamp': datetime.now().isoformat()
                }
            )
        except Exception as e:
            print(f"❌ Failed to add to RAG knowledge base: {e}")
            return False
    
    def _generate_similarity_insights(self, rag_similarity) -> List[str]:
        """Generate insights from RAG similarity analysis"""
        insights = []
        
        if rag_similarity.retrieved_documents:
            insights.append(f"Found {len(rag_similarity.retrieved_documents)} similar documents")
            
            avg_similarity = np.mean(rag_similarity.similarity_scores) if rag_similarity.similarity_scores else 0
            insights.append(f"Average similarity: {avg_similarity:.2f}")
            
            # Check for document type consistency
            doc_types = [doc.get('document_type', 'unknown') for doc in rag_similarity.retrieved_documents]
            if len(set(doc_types)) == 1:
                insights.append(f"All similar documents are of type: {doc_types[0]}")
            else:
                insights.append(f"Similar documents span multiple types: {', '.join(set(doc_types))}")
        
        return insights
    
    def _calculate_enhanced_similarity_score(
        self, 
        original_score: float, 
        rag_similarity
    ) -> float:
        """Calculate enhanced similarity score using RAG insights"""
        if not rag_similarity.retrieved_documents:
            return original_score
        
        # Boost score based on RAG findings
        rag_boost = min(0.2, np.mean(rag_similarity.similarity_scores) * 0.1) if rag_similarity.similarity_scores else 0
        enhanced_score = min(1.0, original_score + rag_boost)
        
        return enhanced_score
    
    def _generate_comprehensive_insights(
        self, 
        classification_result: Dict[str, Any],
        similarity_result: Dict[str, Any],
        authenticity_verification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive insights from all RAG analyses"""
        insights = {
            'classification_confidence': classification_result.get('classification_result', {}).get('confidence', 0),
            'similarity_analysis': {
                'similar_documents': similarity_result.get('rag_similarity_analysis', {}).get('similar_documents_found', 0),
                'enhanced_similarity_score': similarity_result.get('enhanced_similarity_score', 0)
            },
            'authenticity_verification': {
                'verification_confidence': authenticity_verification.get('rag_verification', {}).get('verification_confidence', 0),
                'similar_authentic_documents': authenticity_verification.get('rag_verification', {}).get('similar_authentic_documents', 0)
            },
            'overall_rag_quality': self._calculate_overall_rag_quality(
                classification_result, similarity_result, authenticity_verification
            )
        }
        
        return insights
    
    def _generate_rag_recommendations(
        self, 
        classification_result: Dict[str, Any],
        similarity_result: Dict[str, Any],
        authenticity_verification: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on RAG analysis"""
        recommendations = []
        
        # Classification recommendations
        classification_confidence = classification_result.get('classification_result', {}).get('confidence', 0)
        if classification_confidence < 0.7:
            recommendations.append("Consider manual review due to low classification confidence")
        
        # Similarity recommendations
        similar_docs = similarity_result.get('rag_similarity_analysis', {}).get('similar_documents_found', 0)
        if similar_docs > 3:
            recommendations.append("Multiple similar documents found - verify originality")
        
        # Authenticity recommendations
        auth_verification = authenticity_verification.get('rag_verification', {})
        if auth_verification.get('verification_confidence', 0) < 0.5:
            recommendations.append("Low authenticity verification confidence - additional review recommended")
        
        return recommendations
    
    def _calculate_overall_rag_quality(
        self, 
        classification_result: Dict[str, Any],
        similarity_result: Dict[str, Any],
        authenticity_verification: Dict[str, Any]
    ) -> float:
        """Calculate overall RAG analysis quality score"""
        try:
            # Classification quality
            classification_confidence = classification_result.get('classification_result', {}).get('confidence', 0)
            
            # Similarity quality
            similarity_quality = similarity_result.get('rag_similarity_analysis', {}).get('average_similarity', 0)
            
            # Authenticity quality
            auth_quality = authenticity_verification.get('rag_verification', {}).get('verification_confidence', 0)
            
            # Weighted average
            overall_quality = (
                classification_confidence * 0.4 +
                similarity_quality * 0.3 +
                auth_quality * 0.3
            )
            
            return round(overall_quality, 3)
            
        except Exception:
            return 0.0
    
    def get_rag_system_status(self) -> Dict[str, Any]:
        """Get RAG system status and statistics"""
        try:
            rag_stats = self.rag_service.get_rag_statistics()
            
            return {
                'rag_service': rag_stats,
                'classification_service': self.classification_service.get_model_status(),
                'clone_detection_service': {
                    'status': 'available',
                    'database_path': self.clone_detection_service.db_path
                },
                'ai_clone_service': {
                    'status': 'available',
                    'database_path': self.ai_clone_service.db_path
                },
                'integration_status': 'active',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Failed to get RAG system status: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }


# Global RAG-enhanced classification service instance
rag_enhanced_classification_service = RAGEnhancedClassificationService()
