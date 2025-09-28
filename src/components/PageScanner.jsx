import { useState } from 'react';

export default function PageScanner({ msg, url, onText }) {
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState('');

  const handleScan = async () => {
  setLoading(true);

  // Grab all <p> text on the page
  const paragraphs = Array.from(document.querySelectorAll('p'));
  const pageText = paragraphs.map(p => p.innerText).join('\n\n');
  console.log("Page text to send:", pageText);

  if (onText) onText(pageText);

  try {
    const res = await fetch('http://127.0.0.1:8000/process-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: pageText }),
    });

    const data = await res.json();
    console.log("Agent summary:", data.summary);

    if (onSummary) onSummary(data.summary);

  } catch (err) {
    console.error('Error sending text to backend:', err);
    if (onSummary) onSummary("Error retrieving summary.");
  } finally {
    setLoading(false);
  }
};

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
        }}
        title={url}
      >
        {loading ? 'Scanning...' : url || 'Loading...'}
      </button>
    </div>
  );
}