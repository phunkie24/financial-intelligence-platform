import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function CompanySearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [searching, setSearching] = useState(false)
  const navigate = useNavigate()

  const handleSearch = async (value) => {
    setQuery(value)
    
    if (value.length < 2) {
      setResults([])
      return
    }

    setSearching(true)
    try {
      const response = await fetch(`http://127.0.0.1:8001/api/search?q=${value}`)
      const data = await response.json()
      setResults(data.results || [])
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setSearching(false)
    }
  }

  const handleSelectCompany = (companyName) => {
    // Navigate to company detail page (we'll create this)
    window.location.href = `/company/${companyName}`
    setQuery('')
    setResults([])
  }

  return (
    <div className="bg-slate-800 rounded-xl shadow-xl p-4 border border-slate-700">
      <h3 className="font-semibold mb-3 text-white">🔍 Search Companies</h3>
      
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Search Tesla, Apple..."
          className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        
        {searching && (
          <div className="absolute right-3 top-2.5">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
          </div>
        )}
      </div>

      {/* Search Results Dropdown */}
      {results.length > 0 && (
        <div className="mt-2 bg-slate-700 border border-slate-600 rounded-lg overflow-hidden">
          {results.map((company, idx) => (
            <div
              key={idx}
              onClick={() => handleSelectCompany(company.name)}
              className="p-3 hover:bg-slate-600 cursor-pointer border-b border-slate-600 last:border-b-0 transition-colors"
            >
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-semibold text-white text-sm">{company.name}</p>
                  <p className="text-xs text-slate-400">{company.mention_count} mentions</p>
                </div>
                <span className={`text-xs font-bold px-2 py-1 rounded ${
                  company.avg_sentiment > 0.2 ? 'bg-green-500/20 text-green-400' :
                  company.avg_sentiment < -0.2 ? 'bg-red-500/20 text-red-400' :
                  'bg-slate-600 text-slate-300'
                }`}>
                  {company.avg_sentiment > 0 ? '+' : ''}{(company.avg_sentiment * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* No Results */}
      {query.length >= 2 && !searching && results.length === 0 && (
        <div className="mt-2 p-3 bg-slate-700/50 border border-slate-600 rounded-lg text-center">
          <p className="text-sm text-slate-400">No companies found</p>
        </div>
      )}

      {/* Quick Access */}
      <div className="mt-4">
        <p className="text-xs text-slate-400 mb-2">Quick access:</p>
        <div className="flex flex-wrap gap-2">
          {['Tesla', 'Apple', 'Nvidia', 'Microsoft'].map((name) => (
            <button
              key={name}
              onClick={() => handleSearch(name.toLowerCase())}
              className="px-3 py-1 text-xs bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-full transition-colors border border-slate-600"
            >
              {name}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}