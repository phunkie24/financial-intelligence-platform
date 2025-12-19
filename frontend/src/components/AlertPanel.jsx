import { useState, useEffect } from 'react'

export default function AlertPanel() {
  const [alerts, setAlerts] = useState([])

  useEffect(() => {
    loadAlerts()
  }, [])

  const loadAlerts = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8001/api/alerts?limit=3')
      const data = await response.json()
      setAlerts(data.alerts)
    } catch (error) {
      console.error('Failed to load alerts:', error)
    }
  }

  return (
    <div className="bg-slate-800 rounded-xl shadow-xl p-4 border border-slate-700">
      <h3 className="font-semibold mb-3 text-white">🔔 Alerts</h3>
      <div className="space-y-2">
        {alerts.map((alert) => (
          <div key={alert.id} className={`p-3 rounded-lg text-sm border ${
            alert.severity === 'HIGH' ? 'bg-red-500/10 border-red-500/30 text-red-400' :
            alert.severity === 'MEDIUM' ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400' :
            'bg-blue-500/10 border-blue-500/30 text-blue-400'
          }`}>
            <p className="font-semibold">{alert.company}</p>
            <p className="text-xs opacity-75 mt-1">{alert.message}</p>
          </div>
        ))}
      </div>
    </div>
  )
}