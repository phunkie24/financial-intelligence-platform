import { useState, useEffect } from 'react'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [companies, setCompanies] = useState([])
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [statsRes, companiesRes, docsRes] = await Promise.all([
        fetch('http://127.0.0.1:8001/api/stats').then(r => r.json()),
        fetch('http://127.0.0.1:8001/api/companies?limit=5').then(r => r.json()),
        fetch('http://127.0.0.1:8001/api/documents?limit=3').then(r => r.json())
      ])
      
      setStats(statsRes.stats)
      setCompanies(companiesRes.companies)
      setDocuments(docsRes.documents)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-slate-400">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">📊 Dashboard</h1>

      {/* Stats Grid */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard 
            title="Companies Tracked" 
            value={stats.total_companies} 
            icon="🏢" 
            color="blue" 
          />
          <StatCard 
            title="Articles Analyzed" 
            value={stats.total_articles} 
            icon="📰" 
            color="green" 
          />
          <StatCard 
            title="Documents" 
            value={stats.total_documents} 
            icon="📄" 
            color="purple" 
          />
          <StatCard 
            title="High Risk Alerts" 
            value={stats.high_risk_companies} 
            icon="⚠️" 
            color="red" 
          />
        </div>
      )}

      {/* Top Companies */}
      <div className="bg-slate-800 rounded-xl shadow-xl p-6 border border-slate-700">
        <h2 className="text-xl font-bold mb-4 text-white">Top Tracked Companies</h2>
        <div className="space-y-3">
          {companies.map((company, idx) => (
            <div 
              key={idx} 
              className="flex justify-between items-center p-4 bg-slate-700/50 hover:bg-slate-700 rounded-lg transition-colors cursor-pointer"
            >
              <div>
                <span className="font-semibold text-white">{company.name}</span>
                <p className="text-sm text-slate-400">{company.mention_count} mentions</p>
              </div>
              <span className={`px-4 py-2 rounded-lg text-sm font-bold ${
                company.avg_sentiment > 0.2 ? 'bg-green-100 text-green-800' :
                company.avg_sentiment < -0.2 ? 'bg-red-100 text-red-800' :
                'bg-gray-200 text-gray-800'
              }`}>
                {company.avg_sentiment > 0 ? '+' : ''}{(company.avg_sentiment * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Documents - NOW WITH REAL DATA */}
        <div className="bg-slate-800 rounded-xl shadow-xl p-6 border border-slate-700">
          <h2 className="text-xl font-bold mb-4 text-white">📄 Recent Documents</h2>
          {documents.length > 0 ? (
            <div className="space-y-3">
              {documents.map((doc) => (
                <DocumentItem 
                  key={doc.id}
                  name={doc.filename}
                  company={doc.company}
                  type={doc.type}
                  date={new Date(doc.uploaded).toLocaleDateString()}
                  processed={doc.processed}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-4xl mb-2 opacity-30">📭</div>
              <p className="text-slate-400 text-sm">No documents uploaded yet</p>
            </div>
          )}
        </div>

        {/* System Status */}
        <div className="bg-slate-800 rounded-xl shadow-xl p-6 border border-slate-700">
          <h2 className="text-xl font-bold mb-4 text-white">⚙️ System Status</h2>
          <div className="space-y-3">
            <StatusItem label="Backend API" status="operational" />
            <StatusItem label="Document Processing" status="operational" />
            <StatusItem label="Database" status="operational" />
            <StatusItem label="OCR Engine" status="ready" />
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon, color }) {
  const colors = {
    blue: 'from-blue-600 to-blue-700',
    green: 'from-green-600 to-green-700',
    purple: 'from-purple-600 to-purple-700',
    red: 'from-red-600 to-red-700'
  }

  return (
    <div className="bg-slate-800 rounded-xl shadow-xl p-6 border border-slate-700 hover:border-slate-600 transition-all">
      <div className={`inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br ${colors[color]} rounded-lg text-white text-2xl mb-3 shadow-lg`}>
        {icon}
      </div>
      <p className="text-slate-400 text-sm mb-1">{title}</p>
      <p className="text-3xl font-bold text-white">{value}</p>
    </div>
  )
}

function DocumentItem({ name, company, type, date, processed }) {
  return (
    <div className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg hover:bg-slate-700 transition-all border border-slate-600">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center text-xl border border-blue-500/30">
          📄
        </div>
        <div>
          <p className="font-semibold text-sm text-white">{name}</p>
          <p className="text-xs text-slate-400">{company} • {type}</p>
        </div>
      </div>
      <div className="text-right">
        <span className={`text-xs px-2 py-1 rounded ${
          processed 
            ? 'bg-green-500/20 text-green-400' 
            : 'bg-yellow-500/20 text-yellow-400'
        }`}>
          {processed ? '✅' : '⏳'}
        </span>
        <p className="text-xs text-slate-500 mt-1">{date}</p>
      </div>
    </div>
  )
}

function StatusItem({ label, status }) {
  return (
    <div className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg border border-slate-600">
      <span className="text-sm font-medium text-slate-300">{label}</span>
      <span className="flex items-center gap-2">
        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></span>
        <span className="text-sm text-green-400 font-semibold capitalize">{status}</span>
      </span>
    </div>
  )
}