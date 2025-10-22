/**
 * API Service for Authentia AI Document Analysis
 * Handles all communication with the backend API
 */

import axios from 'axios';

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for document processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for API responses
export interface LayerScore {
  classification: number;
  clone: number;
  crypto: number;
  rag: number;
  metadata: number;
  ai_detection: number;
}

export interface LayerExplanations {
  [key: string]: string;
}

export interface WordExplanation {
  highlight_color: 'green' | 'yellow' | 'red';
  confidence: number;
  explanation: string;
  contributing_layers: string[];
  position: number;
}

export interface HighlightedDocument {
  highlighted_words: [string, string][]; // [word, color_emoji]
  word_explanations: { [key: string]: WordExplanation };
  total_words: number;
}

export interface FinalAssessment {
  authenticity_score: number;
  label: string;
  confidence: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
}

export interface DocumentAnalysis {
  layer_scores: LayerScore;
  layer_explanations: LayerExplanations;
}

export interface AnalysisResult {
  document_id: string;
  filename: string;
  analysis_timestamp: string;
  text_content: string;
  document_analysis: DocumentAnalysis;
  final_assessment: FinalAssessment;
  highlighted_document: HighlightedDocument;
  processing_stats: {
    text_length: number;
    word_count: number;
    processing_time: number;
  };
}

export interface AnalysisHistoryItem {
  document_id: string;
  filename: string;
  timestamp: string;
  authenticity_score: number;
  label: string;
}

export interface LayerInfo {
  name: string;
  description: string;
  weight: number;
  status?: any;
}

// API functions
export const apiService = {
  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<any> {
    const response = await api.get('/health');
    return response.data;
  },

  /**
   * Analyze uploaded document
   */
  async analyzeDocument(file: File): Promise<AnalysisResult> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/analyze-document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * Get highlighting data for a specific document
   */
  async getDocumentHighlights(documentId: string): Promise<{
    document_id: string;
    highlighted_document: HighlightedDocument;
    final_assessment: FinalAssessment;
  }> {
    const response = await api.get(`/document-highlights/${documentId}`);
    return response.data;
  },

  /**
   * Get analysis history
   */
  async getAnalysisHistory(): Promise<{ analyses: AnalysisHistoryItem[] }> {
    const response = await api.get('/analysis-history');
    return response.data;
  },

  /**
   * Get layer information
   */
  async getLayerInfo(): Promise<{
    layers: { [key: string]: LayerInfo };
    system_info: {
      version: string;
      total_layers: number;
      active_layers: number;
    };
  }> {
    const response = await api.get('/layer-info');
    return response.data;
  },
};

// Add request/response interceptors for error handling
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    console.log(`Response from ${response.config.url}:`, response.status);
    return response;
  },
  (error) => {
    console.error('Response error:', error.response?.data || error.message);

    // Handle common error scenarios
    if (error.response?.status === 404) {
      throw new Error('Endpoint not found');
    } else if (error.response?.status === 500) {
      throw new Error('Server error - please try again later');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout - document processing took too long');
    }

    throw error;
  }
);

export default api;