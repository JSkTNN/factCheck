import { useEffect, useState, useRef } from 'react'
import UrlSender from "@/components/UrlSender";
import './App.css'

export default function App() {
  const urlSenderRef = useRef();
  const [url, setUrl] = useState("Loading...");
  const [article, setArticle] = useState("");
  const [show, setShow] = useState(false)
  const [response, setResponse] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/article") // Later change to Render link
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
      <UrlSender url={url} onResponse={setResponse} />
      {response && <p>Backend received: {response}</p>}
    </div>
  )
}
