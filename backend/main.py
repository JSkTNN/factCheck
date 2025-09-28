import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from run_agent import run_credibility_agent

# This line is essential for uvicorn to find the app
app = FastAPI()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Be more specific in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLrequest(BaseModel):
    url: str

@app.post("/process-url")
async def process_url(request: URLrequest):
    url = request.url
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        paragraphs = soup.find_all('p')
        text_content = "\n".join([p.get_text() for p in paragraphs])

        if not text_content.strip():
             return {"error": "Could not extract meaningful text from the URL."}

        analysis_result = await run_credibility_agent(text_content)
        return analysis_result

    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching URL: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

@app.get("/")
async def root():
    return {"message": "FactCheck API is running"}