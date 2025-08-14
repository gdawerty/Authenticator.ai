import React, { useState } from 'react';

const DocumentsSection: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string>('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      setUploadStatus('');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploadStatus('Uploading...');
    // Replace with your backend API endpoint
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      if (response.ok) {
        setUploadStatus('Upload successful!');
      } else {
        setUploadStatus('Upload failed.');
      }
    } catch (error) {
      setUploadStatus('Error uploading file.');
    }
  };

  return (
    <div className="p-8 bg-gray-900 rounded-lg shadow-lg text-white max-w-md mx-auto mt-10">
      <h2 className="text-2xl font-bold mb-4">Upload Document</h2>
      <input
        type="file"
        accept=".pdf,.doc,.docx,.txt"
        onChange={handleFileChange}
        className="mb-4 block w-full text-gray-200"
      />
      <button
        onClick={handleUpload}
        disabled={!selectedFile}
        className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
      >
        Upload
      </button>
      {uploadStatus && <p className="mt-4">{uploadStatus}</p>}
    </div>
  );
};

export default DocumentsSection;
