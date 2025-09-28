from google.adk.agents import Agent
import google.generativeai as genai
import os; os.environ["GOOGLE_API_KEY"] = "AIzaSyCwV6jhaq9DiuUdhSuIdptf0dTBfR57PSU"

def summarize_text(text: str) -> str:
    response = genai.generate_text(prompt=text)
    return response.text  # Make sure to return the text

def fact_check_text(text: str) -> str:
    # Example: simple fact-checking by asking the model to verify statements
    prompt = f"Check the following text for factual accuracy:\n{text}"
    response = genai.generate_text(prompt=prompt)
    return response.text

def provide_proof(checked_text: str) -> str:
    # Example: provide sources or evidence for the fact-checked text
    prompt = f"Provide sources or evidence for the following fact-checked text:\n{checked_text}"
    response = genai.generate_text(prompt=prompt)
    return response.text


root_agent = Agent(
    name="multi_tool_agent",
    model="gemini-2.0-flash",
    description="Agent to summarize, fact-check, and provide proof for text.",
    instruction="You are a helpful agent who can summarize text, fact-check it, and provide sources for your answers.",
    tools=[summarize_text, fact_check_text, provide_proof]
)