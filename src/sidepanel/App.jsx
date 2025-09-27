import React from 'react'
import PageScanner from '../components/PageScanner'

export default function App() {
  return (
    <div style={{ padding: '1rem', fontFamily: 'sans-serif' }}>
      <h1>Sidepanel Scanner</h1>
      <PageScanner msg="Scan this page from sidepanel" />
    </div>
  )
}