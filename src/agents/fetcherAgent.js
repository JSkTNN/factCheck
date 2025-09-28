// Stub fetcher agent
export function fetcherAgent(html, callback) {
  // Simple cleaning for now
  const cleanedText = html.replace(/\s+/g, ' ').trim()
  callback(cleanedText)
}