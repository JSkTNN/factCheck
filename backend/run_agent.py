
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
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))






# --- Load Environment & API Key ---
load_dotenv()
if 'GEMINI_API_KEY' not in os.environ and 'GOOGLE_API_KEY' in os.environ:
    os.environ['GEMINI_API_KEY'] = os.environ['GOOGLE_API_KEY']
if 'GEMINI_API_KEY' not in os.environ:
    raise ValueError("FATAL: GEMINI_API_KEY is missing. Check your .env file.")
WEBSITE_TEXT_PROMPT = ""
# --- Import your root agent and state keys ---
GEMINI_MODEL = "gemini-2.5-flash"
STATE_WEBSITE_TEXT = "website_text"
STATE_CLAIMS_LIST = "claims_list"
STATE_RAW_CLAIMS_OUTPUT = "raw_claims_output"
STATE_CURRENT_INDEX = "current_index"
STATE_CURRENT_CLAIM = "current_claim"
STATE_CURRENT_ANALYSIS = "current_analysis"
STATE_CURRENT_SCORE = "current_score"
STATE_AGGREGATED_RESULTS = "aggregated_results"
STATE_LOOP_STATUS = "loop_status"
STATE_FINAL_ANALYSIS = "final_analysis"
STATE_FINAL_SCORE = "final_score"


# === CONFIGURATION ===
#def webagent(child_conn):
    #WEBSITE_TEXT_PROMPT = child_conn.recv()
    #child_conn.close()
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
    last_event_content = None # Initialize as None to hold the Content object




    print(f"Starting iterative credibility analysis on provided text...\n")




    # 1. Set up session service and runner
    session_service = InMemorySessionService()
    from agent_def.agent import root_agent
    runner = Runner(agent=root_agent, session_service=session_service, app_name=APP_NAME)
   
    # FIX: Initialize STATE_AGGREGATED_RESULTS here to prevent crash if the loop is skipped (0 claims)
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
            # Capture the full Content object of the final event
            if event.content:
                last_event_content = event.content
           
            # Wait 6 seconds after processing an event to avoid rate limiting.
            if event.author:
                await asyncio.sleep(5)




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
        # FIX: Extract the text from the Content object before loading JSON (fixes score discrepancy)
        if isinstance(last_event_content, types.Content) and last_event_content.parts:
            # The Content object holds the text in its first part
            json_string = last_event_content.parts[0].text
       
        final_output_json = json.loads(json_string)
        final_summary = final_output_json.get("final_summary", "Summary could not be parsed.")
        final_score = int(final_output_json.get("final_score", 0))
    except (json.JSONDecodeError, ValueError, TypeError):
        # Print the problematic object for future debugging if needed
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




"""
  if __name__ == "__main__":
    if asyncio.get_event_loop().is_running():
       asyncio.ensure_future(run_credibility_agent(WEBSITE_TEXT_PROMPT))
    else:
        asyncio.run(run_credibility_agent(WEBSITE_TEXT_PROMPT))
"""

def webagent(child_conn):
    WEBSITE_TEXT_PROMPT = child_conn.recv()
    
    if asyncio.get_event_loop().is_running():
       asyncio.ensure_future(run_credibility_agent(WEBSITE_TEXT_PROMPT))
    else:
        asyncio.run(run_credibility_agent(WEBSITE_TEXT_PROMPT))
    child_conn.close()

    #if asyncio.get_event_loop().is_running():
       #asyncio.ensure_future(run_credibility_agent(WEBSITE_TEXT_PROMPT))
    #else:
        #asyncio.run(run_credibility_agent(WEBSITE_TEXT_PROMPT))
