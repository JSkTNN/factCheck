import React, { useEffect, useState } from 'react';
import PageScanner from '@/components/PageScanner';
import './App.css';

export default function App() {
  const [url, setUrl] = useState('Loading...');
  const [pageText, setPageText] = useState('');
  const [summary, setSummary] = useState('');

  // Get current tab URL via Chrome runtime
  useEffect(() => {
    if (!chrome?.runtime) {
      setUrl('Chrome API not available');
      return;
    }

    chrome.runtime.sendMessage({ type: 'GET_CURRENT_TAB_URL' }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('Message failed:', chrome.runtime.lastError.message);
        setUrl('Failed to get URL');
        return;
      }

      if (response?.url) {
        setUrl(response.url);
      } else {
        setUrl('No URL found');
      }
    });
  }, []);

  return (
    <div style={{ padding: '1rem', fontFamily: 'sans-serif' }}>
      <h1>Fact Checker</h1>

      {/* PageScanner handles scanning, but sends text & summary up to App */}
      <PageScanner
        msg="Scan this page for credibility report."
        url={url}
        onText={(text) => setPageText(text)}
        onSummary={(summary) => setSummary(summary)}
      />

      {/* Echo the page text */}
      {pageText && (
        <div style={{ marginTop: '1rem' }}>
          <h3>Page Text:</h3>
          <pre style={{ maxHeight: '200px', overflow: 'auto', background: '#1a1a1a', color: '#fff', padding: '0.5rem' }}>
            {pageText}
          </pre>
        </div>
      )}

      {/* Display AI summary */}
      {summary && (
        <div style={{ marginTop: '1rem' }}>
          <h3>AI Report:</h3>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}