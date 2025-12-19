import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'

export default function DocumentUpload({ onUploadSuccess }) {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [companyName, setCompanyName] = useState('')
  const [documentType, setDocumentType] = useState('earnings_report')

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return

    setUploading(true)
    setProgress(0)

    const formData = new FormData()
    formData.append('file', file)
    if (companyName) formData.append('company_name', companyName)
    formData.append('document_type', documentType)

    try {
      const response = await axios.post('/api/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          setProgress(percentCompleted)
        }
      })

      if (response.data.success) {
        onUploadSuccess(response.data.document_id, response.data.filename)
      }
    } catch (error) {
      console.error('Upload error:', error)
      alert('Upload failed: ' + (error.response?.data?.detail || error.message))
    } finally {
      setUploading(false)
      setProgress(0)
    }
  }, [companyName, documentType, onUploadSuccess])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg']
    },
    maxFiles: 1,
    disabled: uploading
  })

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--primary)' }}>
        Upload Document
      </h2>

      {/* Company Name Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
          Company Name (Optional)
        </label>
        <input
          type="text"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder="e.g., Tesla, Apple, Microsoft"
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
          style={{ borderColor: '#E2E8F0', focusRing: 'var(--secondary)' }}
          disabled={uploading}
        />
      </div>

      {/* Document Type Select */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
          Document Type
        </label>
        <select
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value)}
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
          style={{ borderColor: '#E2E8F0' }}
          disabled={uploading}
        >
          <option value="earnings_report">Earnings Report</option>
          <option value="10k">10-K Annual Report</option>
          <option value="10q">10-Q Quarterly Report</option>
          <option value="8k">8-K Current Report</option>
          <option value="presentation">Investor Presentation</option>
          <option value="press_release">Press Release</option>
          <option value="other">Other</option>
        </select>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'
        } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        
        {uploading ? (
          <div>
            <div className="text-4xl mb-4">⏳</div>
            <p className="text-lg font-semibold mb-2">Uploading...</p>
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <div
                className="h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%`, backgroundColor: 'var(--primary)' }}
              ></div>
            </div>
            <p className="text-sm text-gray-600">{progress}%</p>
          </div>
        ) : isDragActive ? (
          <div>
            <div className="text-4xl mb-4">📥</div>
            <p className="text-lg font-semibold">Drop the file here</p>
          </div>
        ) : (
          <div>
            <div className="text-4xl mb-4">📄</div>
            <p className="text-lg font-semibold mb-2">
              Drag & drop a file here, or click to select
            </p>
            <p className="text-sm text-gray-600">
              Supports PDF, PNG, JPG (max 50MB)
            </p>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-900">
          <strong>🤖 AI Processing:</strong> Your document will be analyzed using PaddleOCR 
          for text extraction and ERNIE AI for intelligent analysis.
        </p>
      </div>
    </div>
  )
}