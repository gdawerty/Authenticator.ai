import axios, { AxiosResponse } from 'axios';
import type { 
  AuthResponse, 
  LoginCredentials, 
  RegisterData, 
  User, 
  Document, 
  AuthenticityAnalysis,
  ChatSession,
  ChatMessage,
  ApiResponse,
  PaginatedResponse,
  RagClassificationResult,
  RagAuthenticityResult,
  RagSimilarContent,
  RagStats
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response: AxiosResponse<ApiResponse<AuthResponse>> = await api.post('/auth/login', credentials);
    return response.data.data!;
  },

  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response: AxiosResponse<ApiResponse<AuthResponse>> = await api.post('/auth/register', data);
    return response.data.data!;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
    localStorage.removeItem('auth_token');
  },

  getCurrentUser: async (): Promise<User> => {
    const response: AxiosResponse<ApiResponse<User>> = await api.get('/auth/me');
    return response.data.data!;
  },

  refreshToken: async (): Promise<string> => {
    const response: AxiosResponse<ApiResponse<{ token: string }>> = await api.post('/auth/refresh');
    return response.data.data!.token;
  },
};

// Documents API
export const documentsApi = {
  uploadDocument: async (file: File, onProgress?: (progress: number) => void): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);

    const response: AxiosResponse<ApiResponse<Document>> = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data.data!;
  },

  getDocuments: async (page: number = 1, limit: number = 20): Promise<PaginatedResponse<Document>> => {
    const response: AxiosResponse<ApiResponse<PaginatedResponse<Document>>> = await api.get(
      `/documents?page=${page}&limit=${limit}`
    );
    return response.data.data!;
  },

  getDocument: async (id: string): Promise<Document> => {
    const response: AxiosResponse<ApiResponse<Document>> = await api.get(`/documents/${id}`);
    return response.data.data!;
  },

  deleteDocument: async (id: string): Promise<void> => {
    await api.delete(`/documents/${id}`);
  },

  analyzeDocument: async (id: string): Promise<AuthenticityAnalysis> => {
    const response: AxiosResponse<ApiResponse<AuthenticityAnalysis>> = await api.post(`/documents/${id}/analyze`);
    return response.data.data!;
  },

  getAnalysis: async (documentId: string): Promise<AuthenticityAnalysis> => {
    const response: AxiosResponse<ApiResponse<AuthenticityAnalysis>> = await api.get(`/documents/${documentId}/analysis`);
    return response.data.data!;
  },
};

// Chat API
export const chatApi = {
  getChatSessions: async (): Promise<ChatSession[]> => {
    const response: AxiosResponse<ApiResponse<ChatSession[]>> = await api.get('/chat/sessions');
    return response.data.data!;
  },

  createChatSession: async (name?: string): Promise<ChatSession> => {
    const response: AxiosResponse<ApiResponse<ChatSession>> = await api.post('/chat/sessions', { name });
    return response.data.data!;
  },

  getChatSession: async (sessionId: string): Promise<ChatSession> => {
    const response: AxiosResponse<ApiResponse<ChatSession>> = await api.get(`/chat/sessions/${sessionId}`);
    return response.data.data!;
  },

  sendMessage: async (sessionId: string, content: string, attachments?: File[]): Promise<ChatMessage> => {
    const formData = new FormData();
    formData.append('content', content);
    
    if (attachments) {
      attachments.forEach((file, index) => {
        formData.append(`attachment_${index}`, file);
      });
    }

    const response: AxiosResponse<ApiResponse<ChatMessage>> = await api.post(
      `/chat/sessions/${sessionId}/messages`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data.data!;
  },

  deleteChatSession: async (sessionId: string): Promise<void> => {
    await api.delete(`/chat/sessions/${sessionId}`);
  },

  renameChatSession: async (sessionId: string, name: string): Promise<ChatSession> => {
    const response: AxiosResponse<ApiResponse<ChatSession>> = await api.patch(`/chat/sessions/${sessionId}`, { name });
    return response.data.data!;
  },
};

// Analysis API
export const analysisApi = {
  analyzeContent: async (content: string, contentType?: string): Promise<AuthenticityAnalysis> => {
    const response: AxiosResponse<ApiResponse<AuthenticityAnalysis>> = await api.post('/analysis/content', {
      content,
      contentType,
    });
    return response.data.data!;
  },

  analyzeFile: async (file: File): Promise<AuthenticityAnalysis> => {
    const formData = new FormData();
    formData.append('file', file);

    const response: AxiosResponse<ApiResponse<AuthenticityAnalysis>> = await api.post('/analysis/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.data!;
  },

  getAnalysisHistory: async (page: number = 1, limit: number = 20): Promise<PaginatedResponse<AuthenticityAnalysis>> => {
    const response: AxiosResponse<ApiResponse<PaginatedResponse<AuthenticityAnalysis>>> = await api.get(
      `/analysis/history?page=${page}&limit=${limit}`
    );
    return response.data.data!;
  },
};

// RAG API
export const ragApi = {
  classifyContent: async (content: string, options?: { threshold?: number; include_similarity?: boolean }): Promise<RagClassificationResult> => {
    const response: AxiosResponse<ApiResponse<RagClassificationResult>> = await api.post('/api/rag/classify', {
      content,
      ...options,
    });
    return response.data.data!;
  },

  analyzeAuthenticity: async (content: string, options?: { threshold?: number; include_details?: boolean }): Promise<RagAuthenticityResult> => {
    const response: AxiosResponse<ApiResponse<RagAuthenticityResult>> = await api.post('/api/rag/analyze_authenticity', {
      content,
      ...options,
    });
    return response.data.data!;
  },

  findSimilarContent: async (content: string, options?: { limit?: number; threshold?: number }): Promise<RagSimilarContent[]> => {
    const response: AxiosResponse<ApiResponse<RagSimilarContent[]>> = await api.post('/api/rag/find_similar', {
      content,
      ...options,
    });
    return response.data.data!;
  },

  getStats: async (): Promise<RagStats> => {
    const response: AxiosResponse<ApiResponse<RagStats>> = await api.get('/api/rag/stats');
    return response.data.data!;
  },

  healthCheck: async (): Promise<{ status: string; timestamp: string }> => {
    const response: AxiosResponse<ApiResponse<{ status: string; timestamp: string }>> = await api.get('/api/rag/health');
    return response.data.data!;
  },
};

export default api;
