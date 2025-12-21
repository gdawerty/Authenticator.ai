// Authentication types and interfaces
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: string;
  subscription?: 'free' | 'pro' | 'enterprise';
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

// Document types
export interface Document {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadedAt: string;
  userId: string;
  status: 'processing' | 'completed' | 'failed';
  authenticityScore?: number;
  analysis?: AuthenticityAnalysis;
}

export interface AuthenticityAnalysis {
  contentId: string;
  layer1Result: LayerResult;
  layer2Result: LayerResult;
  layer3Result: LayerResult;
  layer4Result: LayerResult;
  overallScore: number;
  confidenceLevel: string;
  riskAssessment: RiskAssessment;
  recommendations: string[];
  processingTime: number;
}

export interface LayerResult {
  name: string;
  score: number;
  confidence: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  details: Record<string, any>;
  processingTime?: number;
}

export interface RiskAssessment {
  riskLevel: 'low' | 'moderate' | 'high' | 'critical';
  riskDescription: string;
  confidenceInAssessment: string;
  overallScore: number;
}

// Chat types
export interface ChatSession {
  id: string;
  name: string;
  userId: string;
  createdAt: string;
  updatedAt: string;
  messages: ChatMessage[];
}

export interface ChatMessage {
  id: string;
  sessionId: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  attachments?: DocumentAttachment[];
  analysis?: AuthenticityAnalysis;
}

export interface DocumentAttachment {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

// Upload types
export interface FileUpload {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed';
  error?: string;
}

// RAG types
export interface RagClassificationResult {
  classification: string;
  confidence: number;
  similarityScore?: number;
  details?: {
    human_probability: number;
    ai_probability: number;
    patterns_detected: string[];
  };
}

export interface RagAuthenticityResult {
  isAuthentic: boolean;
  confidence: number;
  riskLevel: 'low' | 'medium' | 'high';
  details?: {
    authenticity_score: number;
    risk_factors: string[];
    validation_checks: Record<string, boolean>;
  };
}

export interface RagSimilarContent {
  content: string;
  similarity: number;
  metadata?: Record<string, any>;
  source?: string;
}

export interface RagStats {
  totalDocuments: number;
  avgProcessingTime: number;
  accuracyRate: number;
  lastUpdated: string;
}
