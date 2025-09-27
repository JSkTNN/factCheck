import { useState } from 'react'
import { fetcherAgent } from '../agents/fetcherAgent'
import { analyzerAgent } from '../agents/analyzerAgent'

export default function PageScanner({ msg, url }) {
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
      {/* Fixed message above the button */}
      <h2>{msg}</h2>

      {/* Button showing the URL */}
      <button
        onClick={handleScan}
        disabled={loading}
        style={{
          width: '250px',          // fixed width
          whiteSpace: 'nowrap',    // prevent wrapping
          overflow: 'hidden',      // hide overflow
          textOverflow: 'ellipsis',// show "..." if too long
          padding: '0.5rem',
        }}
        title={url} // full URL on hover
      >
        {loading ? 'Scanning...' : url || 'Loading...'}
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