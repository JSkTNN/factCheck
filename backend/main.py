import requests # pyright: ignore[reportMissingModuleSource]
from bs4 import BeautifulSoup # pyright: ignore[reportMissingImports]
from fastapi import FastAPI # pyright: ignore[reportMissingImports]
from fastapi.middleware.cors import CORSMiddleware # pyright: ignore[reportMissingImports]
from pydantic import BaseModel # pyright: ignore[reportMissingImports]
from typing import Dict

from multi_tool_agent.agent import root_agent

app = FastAPI()

headers = {'User-Agent': 'Mozilla/5.0'}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #later change to ["chrome-extension://abcd1234"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str

class URLrequest(BaseModel):
    url:str

@app.post("/process-url")
async def process_url(request: URLrequest):
    url = request.url
    try:
        # Parsing page with bs4
        response = requests.get(url, headers=headers)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        elementList = soup.find_all('p')
        for ele in elementList:
            print(ele.text) # Send to AI agent
        print(f"Received URL: {url}")

        response = requests.get(url, timeout=5)
    except Exception as err:
        return {"error": str(err)}
    return {"received_url": request.url}

@app.post("/process-text")
async def process_text(request: TextRequest) -> Dict:
    page_text = request.text
    try:
        agent_output = root_agent.execute(page_text)

        # Handle dict vs string
        if isinstance(agent_output, dict):
            summary = agent_output.get("output_text", str(agent_output))
        else:
            summary = str(agent_output)

        return {"summary": summary}

    except Exception as e:
        return {"error": str(e)}
    
@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}

@app.get("/article")
async def get_article():
    return {"content": "This is text served from FastAPI!"}
