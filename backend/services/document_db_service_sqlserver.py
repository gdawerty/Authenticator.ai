"""
Document Database Service for Authenticator.AI - SQL Server Version
Handles document storage and analysis results in SQL Server
"""

from .sqlserver_db_service import sql_server_db
from typing import Dict, List, Any, Optional
import json

class DocumentDatabaseService:
    """
    Document database service using SQL Server
    """
    
    def __init__(self):
        self.db_service = sql_server_db
    
    def store_document(self, user_id: str, filename: str, content: str, 
                      file_type: str, file_size: int, **kwargs) -> int:
        """
        Store a document in the docs_db database
        
        Args:
            user_id: ID of the user uploading the document
            filename: Name of the file
            content: Text content of the document
            file_type: Type of the file (pdf, txt, etc.)
            file_size: Size of the file in bytes
            **kwargs: Additional metadata
            
        Returns:
            Document ID
        """
        document_data = {
            'filename': filename,
            'original_filename': kwargs.get('original_filename', filename),
            'file_size': file_size,
            'file_type': file_type,
            'file_hash': kwargs.get('file_hash'),
            'upload_path': kwargs.get('upload_path'),
            'content_text': content,
            'metadata': kwargs.get('metadata', {})
        }
        
        return self.db_service.store_document(user_id, document_data)
    
    def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all documents for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            List of user documents
        """
        return self.db_service.get_user_documents(user_id)
    
    def get_document_details(self, document_id: int, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed document information including analysis results
        
        Args:
            document_id: Document ID
            user_id: User ID (for security)
            
        Returns:
            Document details with analysis results and highlights
        """
        return self.db_service.get_document_details(document_id, user_id)
    
    def store_analysis_result(self, document_id: int, analysis_type: str, 
                            result_data: Dict[str, Any], confidence_score: float = None,
                            processing_time: float = None) -> int:
        """
        Store analysis results for a document
        
        Args:
            document_id: Document ID
            analysis_type: Type of analysis (ai_detection, clone_detection, etc.)
            result_data: Analysis result data
            confidence_score: Confidence score of the analysis
            processing_time: Time taken for processing
            
        Returns:
            Analysis result ID
        """
        analysis_data = {
            'analysis_type': analysis_type,
            'result_data': result_data,
            'confidence_score': confidence_score,
            'processing_time': processing_time
        }
        
        return self.db_service.store_analysis_result(document_id, analysis_data)
    
    def store_document_highlights(self, document_id: int, highlights: List[Dict[str, Any]]):
        """
        Store document highlights (phrases marked as AI-generated, etc.)
        
        Args:
            document_id: Document ID
            highlights: List of highlight data
        """
        self.db_service.store_document_highlights(document_id, highlights)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Database statistics
        """
        return self.db_service.get_database_stats()

# Global document database service instance
document_db_service = DocumentDatabaseService()
