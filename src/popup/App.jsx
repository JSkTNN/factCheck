import React, { useEffect, useState } from 'react'
import PageScanner from '../components/PageScanner'
import './App.css'

export default function App() {
  const [url, setUrl] = useState("Loading...")

  // Get current tab URL via Chrome runtime
  useEffect(() => {
    if (!chrome?.runtime) {
      setUrl("Chrome API not available")
      return
    }

    chrome.runtime.sendMessage({ type: "GET_CURRENT_TAB_URL" }, (response) => {
      if (chrome.runtime.lastError) {
        console.error("Message failed:", chrome.runtime.lastError.message)
        setUrl("Failed to get URL")
        return
      }

      if (response?.url) {
        setUrl(response.url)
      } else {
        setUrl("No URL found")
      }
    })
  }, [])

  return (
    <div style={{ width: '300px', padding: '1rem', fontFamily: 'sans-serif' }}>
      <h1>Fact Checker</h1>
      <PageScanner msg="Scan this page for credibility!" />
      <div style={{ marginTop: '1rem' }}>
        <strong>Current URL:</strong>
        <p>{url}</p>
      </div>
    </div>
  )
}