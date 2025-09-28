import React, { useEffect, useState } from 'react';
import PageScanner from '@/components/PageScanner';
import './App.css';

// Simple CSS for the loading spinner
const spinnerStyle = `
  .loader {
    border: 4px solid #f3f3f3; /* Light grey */
    border-top: 4px solid #3498db; /* Blue */
    border-radius: 50%;
    width: 24px;
    height: 24px;
    animation: spin 2s linear infinite;
    margin: 1rem auto;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

export default function App() {
  const [url, setUrl] = useState('Loading...');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

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
      setUrl(response?.url || 'No URL found');
    });
  }, []);

  const handleScan = async () => {
    setIsLoading(true);
    setError(null);
    setAnalysisResult(null);
    try {
      const res = await fetch('http://127.0.0.1:8000/process-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        setAnalysisResult(data);
      }
    } catch (err) {
      console.error('Error sending URL:', err);
      setError('Failed to connect to the backend. Is the server running?');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: '1rem', fontFamily: 'sans-serif', textAlign: 'center' }}>
      <style>{spinnerStyle}</style>
      <h1>Fact Checker</h1>
      <PageScanner
        msg="Scan this page for a credibility report."
        url={url}
        onScan={handleScan}
        loading={isLoading}
      />
      
      {isLoading && (
        <div>
          <div className="loader"></div>
          <p>Analyzing...</p>
        </div>
      )}

      {error && <div style={{ color: 'red', marginTop: '1rem' }}>Error: {error}</div>}
      
      {analysisResult && (
        <div style={{ marginTop: '1rem', textAlign: 'left' }}>
          <h2>Analysis Complete</h2>
          <h3>Final Score: {analysisResult.final_score}/100</h3>
          <p>
            <b>Summary:</b> {analysisResult.final_summary}
          </p>
          <h4>Claims Reviewed:</h4>
          <ul style={{ paddingLeft: '20px' }}>
            {analysisResult.claims.map((item, index) => (
              <li key={index} style={{ marginBottom: '10px' }}>
                <strong>Claim:</strong> {item.claim} <br />
                <strong>Analysis:</strong> {item.analysis} <br />
                <strong>Score:</strong> {item.score}/100
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}