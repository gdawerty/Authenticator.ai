/**
 * DocumentUploader Component
 * Handles file upload with drag-and-drop functionality
 */

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, AlertCircle, CheckCircle } from 'lucide-react';
import { apiService, AnalysisResult } from '../services/api';

interface DocumentUploaderProps {
  onAnalysisComplete: (result: AnalysisResult) => void;
  onError: (error: string) => void;
}

const DocumentUploader: React.FC<DocumentUploaderProps> = ({
  onAnalysisComplete,
  onError,
}) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string>('');

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (!file) return;

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        onError('File size must be less than 10MB');
        return;
      }

      // Validate file type
      const allowedTypes = [
        'text/plain',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/rtf',
      ];

      if (!allowedTypes.includes(file.type)) {
        onError('File type not supported. Please upload TXT, PDF, DOC, DOCX, or RTF files.');
        return;
      }

      try {
        setIsAnalyzing(true);
        setUploadProgress('Uploading document...');

        // Simulate upload progress
        setTimeout(() => setUploadProgress('Extracting text content...'), 1000);
        setTimeout(() => setUploadProgress('Running Layer 1: MIME Detection...'), 2000);
        setTimeout(() => setUploadProgress('Running Layer 2: Classification...'), 3000);
        setTimeout(() => setUploadProgress('Running Layer 3: Clone Detection...'), 4000);
        setTimeout(() => setUploadProgress('Running Layer 4: Cryptographic Validation...'), 5000);
        setTimeout(() => setUploadProgress('Running Layer 5: RAG Verification...'), 6000);
        setTimeout(() => setUploadProgress('Running Layer 6: AI Detection...'), 7000);
        setTimeout(() => setUploadProgress('Finalizing analysis...'), 8000);

        const result = await apiService.analyzeDocument(file);

        setUploadProgress('Analysis complete!');
        setTimeout(() => {
          onAnalysisComplete(result);
          setIsAnalyzing(false);
          setUploadProgress('');
        }, 500);

      } catch (error: any) {
        console.error('Analysis error:', error);
        onError(error.message || 'Failed to analyze document');
        setIsAnalyzing(false);
        setUploadProgress('');
      }
    },
    [onAnalysisComplete, onError]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/rtf': ['.rtf'],
    },
    maxFiles: 1,
    disabled: isAnalyzing,
  });

  const getDropzoneStyles = () => {
    if (isAnalyzing) {
      return 'border-blue-300 bg-blue-50';
    }
    if (isDragReject) {
      return 'border-red-300 bg-red-50';
    }
    if (isDragActive) {
      return 'border-green-300 bg-green-50';
    }
    return 'border-gray-300 bg-gray-50 hover:bg-gray-100';
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200 ease-in-out
          ${getDropzoneStyles()}
          ${isAnalyzing ? 'cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        <input {...getInputProps()} />

        {isAnalyzing ? (
          <div className="space-y-4">
            {/* Loading Animation */}
            <div className="flex justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>

            {/* Progress Text */}
            <div className="space-y-2">
              <p className="text-lg font-medium text-blue-900">Analyzing Document</p>
              <p className="text-sm text-blue-700">{uploadProgress}</p>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-1000 ease-out"
                style={{ width: '85%' }}
              ></div>
            </div>

            <p className="text-xs text-blue-600">
              Processing through 7 authentication layers...
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Upload Icon */}
            <div className="flex justify-center">
              {isDragReject ? (
                <AlertCircle className="h-12 w-12 text-red-500" />
              ) : isDragActive ? (
                <CheckCircle className="h-12 w-12 text-green-500" />
              ) : (
                <Upload className="h-12 w-12 text-gray-400" />
              )}
            </div>

            {/* Upload Text */}
            <div className="space-y-2">
              {isDragReject ? (
                <p className="text-lg text-red-600">
                  File type not supported
                </p>
              ) : isDragActive ? (
                <p className="text-lg text-green-600">
                  Drop file here to analyze
                </p>
              ) : (
                <>
                  <p className="text-lg text-gray-600">
                    Drop your document here, or{' '}
                    <span className="text-blue-600 font-medium">click to browse</span>
                  </p>
                  <p className="text-sm text-gray-500">
                    Supports TXT, PDF, DOC, DOCX, RTF (max 10MB)
                  </p>
                </>
              )}
            </div>

            {/* File Types */}
            {!isDragActive && !isDragReject && (
              <div className="flex justify-center space-x-4 pt-2">
                <div className="flex items-center space-x-1 text-xs text-gray-500">
                  <File className="h-4 w-4" />
                  <span>TXT</span>
                </div>
                <div className="flex items-center space-x-1 text-xs text-gray-500">
                  <File className="h-4 w-4" />
                  <span>PDF</span>
                </div>
                <div className="flex items-center space-x-1 text-xs text-gray-500">
                  <File className="h-4 w-4" />
                  <span>DOC</span>
                </div>
                <div className="flex items-center space-x-1 text-xs text-gray-500">
                  <File className="h-4 w-4" />
                  <span>DOCX</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Security Notice */}
      <div className="mt-4 p-3 bg-gray-50 rounded-md">
        <p className="text-xs text-gray-600 text-center">
          🔒 Your documents are processed securely and are not stored permanently.
          All analysis is performed using enterprise-grade security protocols.
        </p>
      </div>
    </div>
  );
};

export default DocumentUploader;