import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'

export default function CompanyDetail() {
  const { companyName } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadCompanyData()
  }, [companyName])

  const loadCompanyData = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8001/api/company/${companyName}`)
      const json = await response.json()
      setData(json)
    } catch (error) {
      console.error('Failed to load company data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-400">Company not found</p>
        <Link to="/" className="text-blue-400 hover:underline mt-4 inline-block">
          ← Back to Dashboard
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link to="/" className="text-sm text-slate-400 hover:text-blue-400 mb-2 inline-block">
            ← Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-white">{data.company}</h1>
        </div>
        <div className={`px-6 py-3 rounded-xl font-bold text-lg ${
          data.risk.risk_level === 'HIGH' ? 'bg-red-500/20 text-red-400 border-2 border-red-500/30' :
          data.risk.risk_level === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400 border-2 border-yellow-500/30' :
          'bg-green-500/20 text-green-400 border-2 border-green-500/30'
        }`}>
          {data.risk.risk_level} RISK
        </div>
      </div>

      {/* Risk Breakdown */}
      <div className="bg-slate-800 rounded-xl shadow-xl p-6 border border-slate-700">
        <h2 className="text-xl font-bold text-white mb-4">📊 Risk Analysis</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <RiskMetric label="Overall" value={data.risk.overall_risk} />
          <RiskMetric label="Sentiment" value={data.risk.components.sentiment} />
          <RiskMetric label="Frequency" value={data.risk.components.frequency} />
          <RiskMetric label="Credibility" value={data.risk.components.credibility} />
        </div>
      </div>

      {/* Sentiment Timeline */}
      <div className="bg-slate-800 rounded-xl shadow-xl p-6 border border-slate-700">
        <h2 className="text-xl font-bold text-white mb-4">📈 Sentiment Timeline</h2>
        <div className="space-y-2">
          {data.timeline.map((point, idx) => (
            <div key={idx} className="flex items-center gap-4">
              <span className="text-sm text-slate-400 w-24">{point.date}</span>
              <div className="flex-1 h-8 bg-slate-700 rounded-lg overflow-hidden">
                <div 
                  className={`h-full ${point.sentiment > 0 ? 'bg-green-500' : 'bg-red-500'}`}
                  style={{ width: `${Math.abs(point.sentiment) * 100}%` }}
                ></div>
              </div>
              <span className={`text-sm font-bold w-16 text-right ${
                point.sentiment > 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {point.sentiment > 0 ? '+' : ''}{(point.sentiment * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Articles */}
      <div className="bg-slate-800 rounded-xl shadow-xl p-6 border border-slate-700">
        <h2 className="text-xl font-bold text-white mb-4">📰 Recent Articles</h2>
        <div className="space-y-4">
          {data.recent_articles.map((article, idx) => (
            <div key={idx} className="p-4 bg-slate-700/50 rounded-lg border border-slate-600">
              <h3 className="font-semibold text-white mb-2">{article.title}</h3>
              <p className="text-sm text-slate-400 mb-3">{article.content}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-500">{article.source.name}</span>
                <span className={`px-3 py-1 rounded text-xs font-bold ${
                  article.sentiment > 0.2 ? 'bg-green-500/20 text-green-400' :
                  article.sentiment < -0.2 ? 'bg-red-500/20 text-red-400' :
                  'bg-slate-600 text-slate-300'
                }`}>
                  {article.sentiment > 0 ? '+' : ''}{(article.sentiment * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function RiskMetric({ label, value }) {
  return (
    <div className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
      <p className="text-sm text-slate-400 mb-1">{label}</p>
      <p className="text-2xl font-bold text-white">{value.toFixed(1)}</p>
    </div>
  )
}