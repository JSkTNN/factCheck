import asyncio
from multiprocessing import Pipe, Process
"""
from google.adk.cli.utils.agent_loader import AgentLoader
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService 
# FIX: Import Content/Part from the underlying Generative AI types
from google.genai import types 

AGENT_FOLDER_NAME = "multi_tool_agent"  # This is your APP_NAME

async def run_agent_once(query: str):
    # Setup variables
    user_id = "single_run_user"
    session_id = "temp_session"
    APP_NAME = AGENT_FOLDER_NAME
    
    # 1. Load the agent
    root_agent = AgentLoader(agents_dir=".").load_agent(AGENT_FOLDER_NAME)

    # 2. Set up a SessionService and Runner
    session_service = InMemorySessionService()
    
    # ⭐ NEW FIX: Create the session explicitly
    # This ensures 'temp_session' exists before the Runner tries to access it.
    await session_service.create_session(
        app_name=APP_NAME, 
        user_id=user_id,
        session_id=session_id
    )

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=APP_NAME 
    )

    # Create the user message
    new_message = types.Content(
        role='user', 
        parts=[types.Part(text=query)]
    )

    print(f"Running agent '{APP_NAME}' with query: '{query}'")

    # 3. Run the agent and process the stream of events
    final_response = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=new_message
    ):
        # We only care about the final response event
        if event.is_final_response() and event.content and event.content.parts:
            # Extract the text from the parts
            for part in event.content.parts:
                if part.text:
                    final_response += part.text
            
            print("\n--- Agent Final Response ---")
            print(final_response)
            return

    if not final_response:
        print("\nAgent finished, but did not yield a final text response event.")

if __name__ == "__main__":
    input_query = "What is the weather in New York?" # Changed query for easy test
    asyncio.run(run_agent_once(input_query))
"""

def webagent(child_conn):
    # Receive text from main.py
    text = child_conn.recv()
    print("received", text)
    child_conn.close()
    
    