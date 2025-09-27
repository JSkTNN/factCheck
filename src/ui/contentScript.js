import { fetcherAgent } from '../agents/fetcherAgent'
import { analyzerAgent } from '../agents/analyzerAgent'

export function scanCurrentPage() {
  const pageHTML = document.querySelector('article')?.innerHTML || document.body.innerHTML || ''

  fetcherAgent(pageHTML, async (cleanedText) => {
    const result = await analyzerAgent(cleanedText)
    console.log('AI Summary:', result)
  })
}