import asyncio
import os
import json
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai import errors
import sys

# --- Import ADK Agents, Constants, and Tools ---
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

# --- Define Constants ---
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
    """Initializes and runs the credibility agent pipeline and returns the final result."""
    user_id = "test_user"
    session_id = "test_session"
    last_event_content = None

    print(f"Starting iterative credibility analysis...\n")

    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, session_service=session_service, app_name=APP_NAME)

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

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=new_message
        ):
            if event.author:
                print(f"    [LOG] Agent '{event.author}' generated a '{event.__class__.__name__}'")
            if event.content:
                last_event_content = event.content
            if event.author:
                await asyncio.sleep(6) # Reduced sleep time for faster testing

    except Exception as e:
        print(f"❌ An error occurred during the agent run: {e}")
        return {"error": str(e)}

    # --- Process and Return Final Result ---
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
        return {"error": "Failed to parse final agent output."}

    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    aggregated_results = session.state.get(STATE_AGGREGATED_RESULTS, [])

    return {
        "final_summary": final_summary,
        "final_score": final_score,
        "claims": aggregated_results
    }