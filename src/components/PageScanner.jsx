import React from 'react';

export default function PageScanner({ msg, url, onScan, loading }) {
  return (
    <div style={{ padding: '0.5rem' }}>
      <h2>{msg}</h2>
      <button
        onClick={onScan}
        disabled={loading || !url || url.startsWith('chrome')}
        style={{
          width: '250px',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          padding: '0.5rem',
          cursor: loading || !url || url.startsWith('chrome') ? 'not-allowed' : 'pointer',
        }}
        title={url}
      >
        {loading ? 'Scanning...' : 'Scan this page'}
      </button>
    </div>
  );
}