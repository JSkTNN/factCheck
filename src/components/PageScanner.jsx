import React from 'react';
import React from 'react';

export default function PageScanner({ msg, url, onScan, loading }) {
  return (
    <div style={{ padding: '0.5rem' }}>
      <h2>{msg}</h2>
      <button
        onClick={onScan}
        disabled={loading || !url || url.startsWith('chrome')}
        class='btn'
        title={url}
      >
        {loading ? 'Scanning...' : 'Scan this page'}
      </button>
    </div>
  );
}