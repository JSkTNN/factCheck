import requests # pyright: ignore[reportMissingModuleSource]
from bs4 import BeautifulSoup # pyright: ignore[reportMissingImports]
from fastapi import FastAPI # pyright: ignore[reportMissingImports]
from fastapi.middleware.cors import CORSMiddleware # pyright: ignore[reportMissingImports]
from pydantic import BaseModel # pyright: ignore[reportMissingImports]
from multiprocessing import Pipe, Process
from run_agent import webagent
"""
app = FastAPI()

headers = {'User-Agent': 'Mozilla/5.0'}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #later change to ["chrome-extension://abcd1234"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}

@app.get("/article")
async def get_article():
    return {"content": "This is text served from FastAPI!"}
"""

if __name__ == "__main__":
    parent_conn, child_conn = Pipe()

    p = Process(target=webagent, args=(child_conn,))
    p.start()

    text_to_send = "This is the text from main.py"
    print("Main.py sending text to agent...")
    parent_conn.send(text_to_send)

    p.join()
    print("Agent finished processing.")
