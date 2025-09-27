import { useState } from 'react'
import { fetcherAgent } from '../agents/fetcherAgent'
import { analyzerAgent } from '../agents/analyzerAgent'

export default function PageScanner({ msg }) {
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState('')

  const handleScan = () => {
    setLoading(true)
    setSummary('')

    const pageHTML = document.querySelector('article')?.innerHTML || document.body.innerHTML || ''

    fetcherAgent(pageHTML, async (cleanedText) => {
      const result = await analyzerAgent(cleanedText)
      setSummary(result)
      setLoading(false)
    })
  }

  return (
    <div style={{ padding: '0.5rem' }}>
      <h2>{msg}</h2>
      <button onClick={handleScan} disabled={loading}>
        {loading ? 'Scanning...' : 'Scan This Page'}
      </button>
      {summary && (
        <div style={{ marginTop: '1rem' }}>
          <h3>AI Summary:</h3>
          <p>{summary}</p>
        </div>
      )}
    </div>
  )
}