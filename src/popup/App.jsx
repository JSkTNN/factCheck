import { useEffect, useState } from 'react'
import crxLogo from '@/assets/crx.svg'
import reactLogo from '@/assets/react.svg'
import viteLogo from '@/assets/vite.svg'
import HelloWorld from '@/components/HelloWorld'
import './App.css'

export default function App() {
  const [url, setUrl] = useState("Loading...");
  const [article, setArticle] = useState("");
  const [show, setShow] = useState(false)

  useEffect(() => {
    fetch("http://127.0.0.1:8000/article")
      .then(res => res.json())
      .then(data => setArticle(data.content))
      .catch(err => console.error("Error fetching:", err));
  }, []);

  useEffect(() => {
    if (!chrome?.runtime) {
      setUrl("Chrome API not available");
      return;
    }

    chrome.runtime.sendMessage({ type: "GET_CURRENT_TAB_URL" }, (response) => {
      if (chrome.runtime.lastError) {
        console.error("Message failed:", chrome.runtime.lastError.message);
        setUrl("Failed to get URL");
        return;
      }

      if (response?.url) {
        setUrl(response.url);
      } else {
        setUrl("No URL found");
      }
    });
  }, []);

  return (
    <div>
      <a href="https://vite.dev" target="_blank" rel="noreferrer">
        <img src={viteLogo} className="logo" alt="Vite logo" />
      </a>
      <a href="https://reactjs.org/" target="_blank" rel="noreferrer">
        <img src={reactLogo} className="logo react" alt="React logo" />
      </a>
      <a href="https://crxjs.dev/vite-plugin" target="_blank" rel="noreferrer">
        <img src={crxLogo} className="logo crx" alt="crx logo" />
      </a>
      <HelloWorld msg="Vite + React + CRXJS" />
      <h1>{url || "Loading..."}</h1>
    </div>
  )
}
