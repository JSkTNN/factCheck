import { useState } from 'react'
import { fetcherAgent } from '../agents/fetcherAgent'
import { analyzerAgent } from '../agents/analyzerAgent'

export default function PageScanner({ msg, url, onResponse }) {
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState('')

  const sendUrl = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/process-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();

      onResponse(data.received_url);
    } catch (err) {
      console.error("Error sending URL:", err);
    }
  };

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
        onClick={sendUrl}
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