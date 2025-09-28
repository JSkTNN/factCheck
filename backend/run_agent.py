import asyncio
import os
import json
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai import errors
from multiprocessing import Pipe, Process
import sys
import os

# --- Import ADK Agents, Constants, and Tools GLOBALLY ---
# This ensures the child process has access to these definitions.
from agent_def.agent import (
    root_agent, 
    STATE_WEBSITE_TEXT, 
    STATE_AGGREGATED_RESULTS,
)

# --- Load Environment & API Key ---
load_dotenv()
if 'GEMINI_API_KEY' not in os.environ and 'GOOGLE_API_KEY' in os.environ:
    os.environ['GEMINI_API_KEY'] = os.environ['GOOGLE_API_KEY']
if 'GEMINI_API_KEY' not in os.environ:
    raise ValueError("FATAL: GEMINI_API_KEY is missing. Check your .env file.")

# --- Define Constants (Globally) ---
APP_NAME = "credibility_checker"


def score_to_color(score: int) -> str:
    """Converts a numerical score (0-100) to a color-coded string."""
    if score >= 80:
        return f"🟢 High Credibility ({score}/100)"
    elif score >= 50:
        return f"🟡 Medium Credibility ({score}/100)"
    else:
        return f"🔴 Low Credibility ({score}/100)"


async def run_credibility_agent(website_text: str):
    """Initializes and runs the credibility agent pipeline with provided text."""
    user_id = "test_user"
    session_id = "test_session"
    last_event_content = None

    print(f"Starting iterative credibility analysis on provided text...\n")

    # 1. Set up session service and runner
    session_service = InMemorySessionService()
    # root_agent is now guaranteed to be defined globally
    runner = Runner(agent=root_agent, session_service=session_service, app_name=APP_NAME)
    
    # Initialize state
    initial_state = {
        STATE_WEBSITE_TEXT: website_text,
        STATE_AGGREGATED_RESULTS: [],
    }
    
    await session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id, state=initial_state
    )

    new_message = types.Content(
        role='user',
        parts=[types.Part(text="Start the iterative credibility analysis.")]
    )

    # 2. Run the agent
    try:
        print("--- Starting agent run ---")
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=new_message
        ):
            if event.author:
                print(f"    [LOG] Agent '{event.author}' generated a '{event.__class__.__name__}'")
            if event.content:
                last_event_content = event.content
            
            # Wait 5 seconds after processing an event to avoid rate limiting.
            if event.author:
                await asyncio.sleep(6)  # Slightly more than 5s to be safe

    except Exception as e:
        print(f"❌ An error occurred during the agent run: {e}")
        return

    # 3. Retrieve and display the final results
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    aggregated_results = session.state.get(STATE_AGGREGATED_RESULTS, [])
    
    final_summary = "Summary not found."
    final_score = 0
    
    try:
        json_string = ""
        if isinstance(last_event_content, types.Content) and last_event_content.parts:
            json_string = last_event_content.parts[0].text
        
        final_output_json = json.loads(json_string)
        final_summary = final_output_json.get("final_summary", "Summary could not be parsed.")
        final_score = int(final_output_json.get("final_score", 0))
    except (json.JSONDecodeError, ValueError, TypeError):
        print(f"\n Could not parse final JSON output. Last content: {last_event_content}")

    final_color = score_to_color(final_score)

    print("\n" + "="*60)
    print("           CREDIBILITY ANALYSIS COMPLETE")
    print("="*60)

    print("\n### Claim-by-Claim Breakdown ###")
    if aggregated_results:
        for i, result in enumerate(aggregated_results):
            claim_score_color = score_to_color(result.get('score', 0))
            print(f"\n{i+1}. Claim: \"{result.get('claim', 'N/A')}\"")
            print(f"    Analysis: {result.get('analysis', 'N/A')}")
            print(f"    Score: {claim_score_color}")
    else:
        print("No individual claims were analyzed.")

    print("\n" + "-"*60)
    print("\n### Final Assessment ###")
    print(f"\nOverall Summary: {final_summary}")
    print(f"\nFinal Score: {final_color}")
    print("="*60)


def webagent(child_conn):
    """Target function for the multiprocessing thread to run the agent."""
    text_to_process = child_conn.recv()
    
    # This function must be run by asyncio.run in the new process.
    try:
        asyncio.run(run_credibility_agent(text_to_process))
    except Exception as e:
        # Print a clear error message from the child process
        print(f"Agent Process Error in run_agent.py: {e}")
    finally:
        child_conn.close()

# Note: The original __main__ block is in main.py, so we leave this file clean.