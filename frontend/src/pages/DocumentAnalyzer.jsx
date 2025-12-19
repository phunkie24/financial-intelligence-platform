import { useState, useEffect } from 'react'

export default function DocumentAnalyzer() {
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [documents, setDocuments] = useState([])
  const [companyName, setCompanyName] = useState('')
  const [documentType, setDocumentType] = useState('earnings_report')

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8001/api/documents')
      const data = await response.json()
      setDocuments(data.documents || [])
    } catch (error) {
      console.error('Failed to load documents:', error)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    // Validate file type
    const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg']
    if (!validTypes.includes(file.type)) {
      alert('Only PDF and image files (PNG, JPG) are supported')
      return
    }

    // Validate file size (50MB)
    if (file.size > 50 * 1024 * 1024) {
      alert('File too large. Maximum size is 50MB')
      return
    }

    setUploading(true)
    setUploadResult(null)
    
    const formData = new FormData()
    formData.append('file', file)
    if (companyName) formData.append('company_name', companyName)
    formData.append('document_type', documentType)

    try {
      const response = await fetch('http://127.0.0.1:8001/api/documents/upload', {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Upload failed')
      }

      const data = await response.json()
      setUploadResult(data)
      
      // Reload documents list
      setTimeout(() => loadDocuments(), 1000)
      
    } catch (error) {
      alert('Upload failed: ' + error.message)
    } finally {
      setUploading(false)
      // Reset file input
      e.target.value = ''
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">📄 Document Analyzer</h1>
      
      {/* Upload Form */}
      <div className="bg-slate-800 rounded-xl shadow-xl p-6 border border-slate-700">
        <h2 className="text-xl font-semibold text-white mb-4">Upload Financial Document</h2>
        <p className="text-slate-400 mb-6">
          Upload earnings reports, 10-Ks, or investor presentations for AI-powered analysis
          with PaddleOCR text extraction and ERNIE sentiment analysis.
        </p>

        {/* Company Name */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Company Name (Optional)
          </label>
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="e.g., Tesla, Apple, Microsoft"
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={uploading}
          />
        </div>

        {/* Document Type */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Document Type
          </label>
          <select
            value={documentType}
            onChange={(e) => setDocumentType(e.target.value)}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={uploading}
          >
            <option value="earnings_report">Earnings Report</option>
            <option value="10k">10-K Annual Report</option>
            <option value="10q">10-Q Quarterly Report</option>
            <option value="8k">8-K Current Report</option>
            <option value="presentation">Investor Presentation</option>
            <option value="press_release">Press Release</option>
            <option value="financial_statement">Financial Statement</option>
            <option value="other">Other</option>
          </select>
        </div>
        
        {/* Upload Area */}
        <div className="border-2 border-dashed border-slate-600 rounded-xl p-12 text-center hover:border-blue-500 transition-colors bg-slate-700/30">
          <input
            type="file"
            onChange={handleFileUpload}
            accept=".pdf,.png,.jpg,.jpeg"
            className="hidden"
            id="file-upload"
            disabled={uploading}
          />
          <label htmlFor="file-upload" className={`cursor-pointer ${uploading ? 'opacity-50' : ''}`}>
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mx-auto mb-4"></div>
                <p className="text-lg font-semibold text-white">Uploading...</p>
              </>
            ) : (
              <>
                <div className="text-6xl mb-4">📄</div>
                <p className="text-lg font-semibold text-white mb-2">
                  Drop files here or click to upload
                </p>
                <p className="text-sm text-slate-400">
                  Supports PDF, PNG, JPG (max 50MB)
                </p>
              </>
            )}
          </label>
        </div>

        {/* Upload Result */}
        {uploadResult && (
          <div className="mt-4 p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
            <p className="text-green-400 font-semibold mb-2">✅ Upload Successful!</p>
            <div className="text-sm text-slate-300 space-y-1">
              <p>• Document ID: {uploadResult.document_id}</p>
              <p>• Filename: {uploadResult.filename}</p>
              <p>• Size: {uploadResult.file_size_mb} MB</p>
              <p>• Status: {uploadResult.status}</p>
            </div>
            <div className="mt-3 text-xs text-slate-400">
              <p className="font-semibold mb-1">Next Steps:</p>
              {uploadResult.next_steps?.map((step, idx) => (
                <p key={idx}>• {step}</p>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Recent Documents */}
      <div className="bg-slate-800 rounded-xl shadow-xl p-6 border border-slate-700">
        <h2 className="text-xl font-semibold text-white mb-4">📋 Uploaded Documents</h2>
        
        {documents.length > 0 ? (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div key={doc.id} className="p-4 bg-slate-700/50 rounded-lg border border-slate-600 hover:bg-slate-700 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center text-2xl border border-blue-500/30">
                      📄
                    </div>
                    <div>
                      <p className="font-semibold text-white">{doc.filename}</p>
                      <p className="text-sm text-slate-400">
                        {doc.company || 'Unknown Company'} • {doc.type}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`px-3 py-1 rounded-lg text-xs font-bold ${
                      doc.processed 
                        ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                        : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                    }`}>
                      {doc.processed ? '✅ Processed' : '⏳ Processing'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-6xl mb-4 opacity-30">📭</div>
            <p className="text-slate-400">No documents uploaded yet</p>
            <p className="text-sm text-slate-500 mt-2">Upload your first financial document to get started</p>
          </div>
        )}
      </div>
    </div>
  )
}