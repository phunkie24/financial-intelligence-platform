import { useState, useEffect } from 'react'
import { API_ENDPOINTS } from '../config'

export default function CompareReports() {
  const [documents, setDocuments] = useState([])
  const [selectedDocs, setSelectedDocs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.documents)
      const data = await response.json()
      setDocuments(data.documents.filter(doc => doc.processed))
    } catch (error) {
      console.error('Failed to load documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleDocument = (docId) => {
    if (selectedDocs.includes(docId)) {
      setSelectedDocs(selectedDocs.filter(id => id !== docId))
    } else {
      if (selectedDocs.length >= 3) {
        alert('You can compare up to 3 documents at once')
        return
      }
      setSelectedDocs([...selectedDocs, docId])
    }
  }

  const getSelectedDocuments = () => {
    return documents.filter(doc => selectedDocs.includes(doc.id))
  }

  const extractCompanyFromFilename = (filename) => {
    // Try to extract company name from filename pattern: CompanyName_Q4_2024_Earnings_Report.pdf
    const match = filename.match(/^([A-Za-z]+)_/)
    return match ? match[1] : 'Unknown'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center text-2xl">
          🔄
        </div>
        <h1 className="text-3xl font-bold text-white">Compare Financial Reports</h1>
      </div>
      
      {/* Instructions */}
      <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
        <p className="text-blue-400 text-sm">
          💡 <strong>Select 2-3 documents</strong> below to compare their financial metrics, 
          risk levels, and extracted data side-by-side.
        </p>
      </div>

      {/* Document Selection */}
      <div className="bg-slate-800 rounded-xl shadow-xl p-6 border border-slate-700">
        <h2 className="text-xl font-bold mb-4 text-white">
          Select Documents <span className="text-slate-400 text-base font-normal">({selectedDocs.length}/3 selected)</span>
        </h2>
        
        {documents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {documents.map((doc) => {
              const company = doc.company !== 'Unknown' ? doc.company : extractCompanyFromFilename(doc.filename)
              return (
                <div
                  key={doc.id}
                  onClick={() => toggleDocument(doc.id)}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedDocs.includes(doc.id)
                      ? 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/20'
                      : 'border-slate-600 bg-slate-700/50 hover:border-slate-500 hover:bg-slate-700'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-xl flex-shrink-0 ${
                        selectedDocs.includes(doc.id) 
                          ? 'bg-blue-500/20 border border-blue-500/30' 
                          : 'bg-slate-600/50 border border-slate-600'
                      }`}>
                        📄
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-bold text-white text-base truncate">{company}</p>
                        <p className="text-xs text-slate-400 truncate">{doc.filename}</p>
                      </div>
                    </div>
                    <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 ml-2 ${
                      selectedDocs.includes(doc.id)
                        ? 'border-blue-500 bg-blue-500'
                        : 'border-slate-500'
                    }`}>
                      {selectedDocs.includes(doc.id) && (
                        <span className="text-white text-sm font-bold">✓</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-600">
                    <span className="text-slate-400 capitalize">{doc.type.replace(/_/g, ' ')}</span>
                    <span className="text-slate-500">
                      {new Date(doc.uploaded).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-6xl mb-4 opacity-30">📭</div>
            <p className="text-slate-400">No processed documents available</p>
            <p className="text-sm text-slate-500 mt-2">
              Upload and process documents first
            </p>
          </div>
        )}
      </div>

      {/* Comparison View - RESPONSIVE GRID */}
      {selectedDocs.length >= 2 && (
        <div className="bg-slate-800 rounded-xl shadow-xl p-6 border border-slate-700">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center text-xl">
              📊
            </div>
            <h2 className="text-xl font-bold text-white">
              Comparison <span className="text-slate-400 text-base font-normal">({selectedDocs.length} documents)</span>
            </h2>
          </div>
          
          {/* FIXED RESPONSIVE GRID - 2 columns max */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {getSelectedDocuments().map((doc) => {
              const company = doc.company !== 'Unknown' ? doc.company : extractCompanyFromFilename(doc.filename)
              return (
                <div key={doc.id} className="bg-slate-700/50 rounded-xl p-5 border border-slate-600 hover:border-slate-500 transition-all">
                  {/* Header */}
                  <div className="flex items-center justify-between mb-4 pb-4 border-b border-slate-600">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center text-2xl font-bold text-white flex-shrink-0">
                        {company.charAt(0)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-bold text-white text-lg truncate">{company}</h3>
                        <p className="text-xs text-slate-400">Q4 2024 Report</p>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleDocument(doc.id)
                      }}
                      className="text-red-400 hover:text-red-300 hover:bg-red-500/10 w-8 h-8 rounded-lg flex items-center justify-center transition-colors flex-shrink-0"
                      title="Remove"
                    >
                      ✕
                    </button>
                  </div>
                  
                  {/* Document Info */}
                  <div className="space-y-3 mb-4">
                    <CompareMetric 
                      label="Document" 
                      value={doc.filename.length > 35 ? doc.filename.substring(0, 35) + '...' : doc.filename}
                      tooltip={doc.filename}
                    />
                    <CompareMetric 
                      label="Type" 
                      value={doc.type.replace(/_/g, ' ')} 
                      badge
                    />
                    <CompareMetric 
                      label="Size" 
                      value={doc.file_size_mb ? `${doc.file_size_mb} MB` : '0 MB'} 
                    />
                    <CompareMetric 
                      label="OCR Quality" 
                      value={doc.ocr_confidence ? `${(doc.ocr_confidence * 100).toFixed(0)}%` : '95%'}
                      isPercentage
                      percentage={doc.ocr_confidence ? doc.ocr_confidence * 100 : 95}
                    />
                    <CompareMetric 
                      label="Uploaded" 
                      value={new Date(doc.uploaded).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric' 
                      })} 
                    />
                  </div>

                  {/* Extracted Metrics */}
                  <div className="mt-4 pt-4 border-t border-slate-600">
                    <p className="text-xs font-semibold text-slate-300 mb-3 flex items-center gap-2">
                      <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                      Extracted Metrics
                    </p>
                    <div className="space-y-2">
                      <CompareMetric label="Revenue" value="Coming soon" upcoming />
                      <CompareMetric label="Net Profit" value="Coming soon" upcoming />
                      <CompareMetric label="Risk Level" value="Coming soon" upcoming />
                      <CompareMetric label="Sentiment" value="Coming soon" upcoming />
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {/* AI Insights - Full Width Below */}
          <div className="mt-6 bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-xl p-5">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-xl flex-shrink-0">
                🤖
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-purple-300 mb-2">
                  AI-Powered Insights
                </h3>
                <p className="text-sm text-slate-400 mb-3">
                  Advanced comparison analysis will be available once PaddleOCR extraction 
                  and ERNIE AI analysis are fully integrated.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
                  <InsightItem icon="📈" text="Financial metrics trends" />
                  <InsightItem icon="⚠️" text="Risk level comparison" />
                  <InsightItem icon="💬" text="Sentiment analysis" />
                  <InsightItem icon="🔍" text="Key differences" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedDocs.length === 1 && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 text-center">
          <p className="text-yellow-400 text-sm">
            ⚠️ Select at least one more document to start comparing
          </p>
        </div>
      )}

      {selectedDocs.length === 0 && documents.length > 0 && (
        <div className="bg-slate-700/30 border border-slate-600 rounded-xl p-6 text-center">
          <div className="text-5xl mb-3">👆</div>
          <p className="text-slate-300 font-medium">Select documents above to begin comparison</p>
          <p className="text-slate-500 text-sm mt-1">Choose 2-3 financial reports to analyze</p>
        </div>
      )}
    </div>
  )
}

function CompareMetric({ label, value, badge, isPercentage, percentage, upcoming, tooltip }) {
  return (
    <div className="flex justify-between items-center" title={tooltip}>
      <span className="text-slate-400 text-xs">{label}:</span>
      {badge ? (
        <span className="bg-slate-600 px-2 py-0.5 rounded text-xs text-white font-medium capitalize">
          {value}
        </span>
      ) : isPercentage ? (
        <div className="flex items-center gap-2">
          <div className="w-16 h-1.5 bg-slate-600 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all ${
                percentage >= 90 ? 'bg-green-500' : 
                percentage >= 70 ? 'bg-yellow-500' : 
                'bg-red-500'
              }`}
              style={{ width: `${percentage}%` }}
            ></div>
          </div>
          <span className="text-white font-medium text-xs">{value}</span>
        </div>
      ) : upcoming ? (
        <span className="text-slate-500 italic text-xs">{value}</span>
      ) : (
        <span className="text-white font-medium text-xs truncate max-w-[200px]" title={value}>{value}</span>
      )}
    </div>
  )
}

function InsightItem({ icon, text }) {
  return (
    <div className="flex items-center gap-2 text-sm text-slate-400">
      <span className="text-lg">{icon}</span>
      <span>{text}</span>
    </div>
  )
}