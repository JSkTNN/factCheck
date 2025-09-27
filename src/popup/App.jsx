import React from 'react'
import PageScanner from '../components/PageScanner'

export default function App() {
  return (
    <div style={{ width: '300px', padding: '1rem', fontFamily: 'sans-serif' }}>
      <h1>Extension Popup</h1>
      <PageScanner msg="Scan this page from popup" />
    </div>
  )
}
