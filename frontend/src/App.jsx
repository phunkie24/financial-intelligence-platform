import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Dashboard from './pages/Dashboard'
import DocumentAnalyzer from './pages/DocumentAnalyzer'
import DocumentChat from './pages/DocumentChat'
import CompareReports from './pages/CompareReports'
import CompanySearch from './components/CompanySearch'
import AlertPanel from './components/AlertPanel'
import CompanyDetail from './pages/CompanyDetail'
import './index.css'

export default function App() {
  const [currentDate, setCurrentDate] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentDate(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <Router>
      <div className="min-h-screen bg-[#0f172a]">
        {/* Header */}
        <header className="bg-gradient-to-r from-slate-800 to-slate-900 text-white shadow-xl border-b border-slate-700">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <div className="flex justify-between items-center">
              <div>
                <Link to="/" className="hover:opacity-80 transition-opacity">
                  <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                    💼 Financial Intelligence Platform
                  </h1>
                  <p className="text-sm mt-1 text-slate-400">
                    AI-Powered Document Analysis with ERNIE & PaddleOCR
                  </p>
                </Link>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-400">
                  {currentDate.toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </p>
                <p className="text-xl font-bold text-white">
                  {currentDate.toLocaleTimeString()}
                </p>
              </div>
            </div>

            {/* Navigation */}
            <nav className="mt-6 flex gap-2">
              <NavLink to="/">📊 Dashboard</NavLink>
              <NavLink to="/documents">📄 Documents</NavLink>
              <NavLink to="/compare">🔄 Compare</NavLink>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="grid grid-cols-12 gap-6">
            {/* Sidebar */}
            <div className="col-span-12 lg:col-span-3 space-y-4">
              <CompanySearch />
              <AlertPanel />
            </div>

            {/* Main Content */}
            <div className="col-span-12 lg:col-span-9">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/documents" element={<DocumentAnalyzer />} />
                <Route path="/document-chat/:documentId" element={<DocumentChat />} />
                <Route path="/compare" element={<CompareReports />} />
                <Route path="/company/:companyName" element={<CompanyDetail />} />
              </Routes>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 py-6 text-center text-sm text-slate-500 bg-slate-900 border-t border-slate-800">
          <p>Built with 🤖 ERNIE AI + 📸 PaddleOCR | Fine-tuned with LoRA & QLoRA</p>
          <p className="mt-1">
            <a href="https://github.com/phunkie24/financial-intelligence-platform" 
               className="text-blue-400 hover:text-blue-300 transition-colors"
               target="_blank"
               rel="noopener noreferrer">
              GitHub Repository
            </a>
            {' • '}
            <a href="http://127.0.0.1:8001/docs" 
               className="text-blue-400 hover:text-blue-300 transition-colors"
               target="_blank"
               rel="noopener noreferrer">
              API Docs
            </a>
          </p>
        </footer>
      </div>
    </Router>
  )
}

function NavLink({ to, children }) {
  return (
    <Link
      to={to}
      className="px-4 py-2 rounded-lg font-medium text-sm text-slate-300 hover:text-white hover:bg-slate-700 transition-all"
    >
      {children}
    </Link>
  )
}