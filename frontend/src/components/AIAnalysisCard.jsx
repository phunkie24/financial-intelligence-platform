export default function AIAnalysisCard({ analysis }) {
  if (!analysis) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500">No analysis available</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-xl font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--primary)' }}>
        <span>🤖</span>
        AI Analysis Summary
      </h3>

      {/* Sentiment */}
      {analysis.sentiment_score !== undefined && (
        <div className="mb-4 p-4 rounded-lg" style={{ backgroundColor: '#F8FAFC' }}>
          <div className="flex justify-between items-center">
            <span className="font-semibold">Sentiment:</span>
            <span className={`px-3 py-1 rounded font-bold ${
              analysis.sentiment_score > 0.3 ? 'bg-green-200 text-green-900' :
              analysis.sentiment_score < -0.3 ? 'bg-red-200 text-red-900' :
              'bg-gray-200 text-gray-900'
            }`}>
              {analysis.sentiment_label?.toUpperCase() || 'NEUTRAL'}
            </span>
          </div>
          <div className="mt-2">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="h-2 rounded-full"
                style={{
                  width: `${Math.abs(analysis.sentiment_score) * 100}%`,
                  backgroundColor: analysis.sentiment_score > 0 ? '#10B981' : '#EF4444'
                }}
              ></div>
            </div>
          </div>
        </div>
      )}

      {/* Key Insights */}
      {analysis.ai_insights && (
        <div className="space-y-2">
          {Object.entries(analysis.ai_insights).map(([key, value]) => (
            <div key={key} className="flex justify-between items-center py-2 border-b">
              <span className="text-sm text-gray-600 capitalize">{key.replace(/_/g, ' ')}:</span>
              <span className="font-semibold">{String(value)}</span>
            </div>
          ))}
        </div>
      )}

      {/* Processing Info */}
      <div className="mt-4 pt-4 border-t text-xs text-gray-500">
        <p>Analyzed with: {analysis.model_used || 'ERNIE 4.5'}</p>
        {analysis.processing_time && (
          <p>Processing time: {analysis.processing_time.toFixed(2)}s</p>
        )}
      </div>
    </div>
  )
}