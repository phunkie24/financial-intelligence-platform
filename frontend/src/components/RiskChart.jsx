import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer } from 'recharts'

export default function RiskChart({ risk }) {
  const data = [
    { factor: 'Sentiment', value: risk.components.sentiment_score },
    { factor: 'Frequency', value: risk.components.frequency_score },
    { factor: 'Recency', value: risk.components.recency_score },
    { factor: 'Credibility', value: risk.components.credibility_score },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={data}>
        <PolarGrid />
        <PolarAngleAxis dataKey="factor" />
        <Radar dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
      </RadarChart>
    </ResponsiveContainer>
  )
}
