export default function UrlSender({ url, onResponse }) {
  const sendUrl = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/process-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();

      onResponse(data.received_url);
    } catch (err) {
      console.error("Error sending URL:", err);
    }
  };

  return (
    <button onClick={sendUrl} >
        Go!
    </button>
  );
}
