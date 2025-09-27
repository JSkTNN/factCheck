import { useState } from 'react'

export default function PageScanner({ msg, url }) {
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState('')

  const handleScan = async () => {
    setLoading(true)
    setSummary('')

    // Grab page text
    const pageText = document.querySelector('article')?.innerText || document.body.innerText || ''

    try {
      const res = await fetch("http://127.0.0.1:8000/process-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: pageText }),
      })
      const data = await res.json()
      setSummary(data.summary || "No summary returned")
    } catch (err) {
      console.error("Error sending text:", err)
      setSummary("Failed to get summary from backend")
    }

    setLoading(false)
  }

  return (
    <div style={{ padding: '0.5rem', textAlign: 'center' }}>
      <h2>{msg}</h2>

      <button
        onClick={handleScan}
        disabled={loading}
        style={{
          width: '250px',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          padding: '0.5rem',
          margin: '1rem auto',
          display: 'block',
        }}
        title={url}
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