import json
import re 
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent 
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

# --- Constants & State Keys ---
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

# --- Tools ---

def process_next_claim(tool_context: ToolContext):
    """
    Gets the next claim from the claims_list based on the current_index.
    Updates the state with the current claim and increments the index.
    Returns 'finished' if no claims are left, otherwise 'continue'.
    """
    claims = tool_context.state.get(STATE_CLAIMS_LIST, [])
    index = tool_context.state.get(STATE_CURRENT_INDEX, 0)

    if index < len(claims):
        current_claim = claims[index]
        print(f"   [Tool Call] Processing claim {index + 1}/{len(claims)}: '{current_claim[:50]}...'")
        tool_context.actions.state_delta = {
            STATE_CURRENT_CLAIM: current_claim,
            STATE_CURRENT_INDEX: index + 1,
        }
        return {"status": "continue"}
    else:
        print("   [Tool Call] No more claims to process.")
        return {"status": "finished"}

process_next_claim_tool = FunctionTool(process_next_claim)

def parse_raw_claims(tool_context: ToolContext):
    """
    Manually parses the raw JSON string output from the LLM into a list,
    by using regex to find the array structure within conversational text.
    """
    raw_output = tool_context.state.get(STATE_RAW_CLAIMS_OUTPUT, "[]")
    
    try:
        # Use regex to find and extract the outermost JSON array structure (the FIX for conversational models)
        json_match = re.search(r'(\[.*\])', raw_output, re.DOTALL)
        
        if json_match:
            clean_output = json_match.group(1)
        else:
            print("   [Tool Call] Regex failed to find array, attempting raw JSON load.")
            clean_output = raw_output.strip().strip('`').strip('json').strip()
        
        claims_list = json.loads(clean_output)
        
        if not isinstance(claims_list, list):
            claims_list = [claims_list]
            
        # Ensure every item in the list is explicitly converted to a string (the FIX for slicing errors)
        claims_list = [str(item) for item in claims_list] 

        print(f"   [Tool Call] Successfully parsed {len(claims_list)} claims.")
        
        tool_context.actions.state_delta = {
            STATE_CLAIMS_LIST: claims_list,
        }
    except json.JSONDecodeError as e:
        print(f"   [Tool Call] ERROR parsing JSON claims: {e}. Output used: '{raw_output[:50]}...'")
        tool_context.actions.state_delta = {
            STATE_CLAIMS_LIST: [],
        }
        
    return {"status": "claims parsed"}

parse_claims_tool = FunctionTool(parse_raw_claims)


def append_result_to_state(
    tool_context: ToolContext, claim: str, analysis: str, score: str
):
    """Appends the analysis of a single claim to the aggregated results list."""
    aggregated_results = tool_context.state.get(STATE_AGGREGATED_RESULTS, [])
    
    new_result = {"claim": claim, "analysis": analysis, "score": int(score)} 
    
    aggregated_results.append(new_result)
    
    tool_context.actions.state_delta = {
        STATE_AGGREGATED_RESULTS: aggregated_results 
    }
    return {"status": "Result appended."}

append_result_tool = FunctionTool(append_result_to_state)

def exit_loop(tool_context: ToolContext):
    """Signals that the analysis is complete and the LoopAgent should terminate."""
    print(f"   [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {"status": "Loop exit signaled."}

exit_loop_tool = FunctionTool(exit_loop)


# === AGENT DEFINITIONS ===

# Agent 1: Extracts claims from the full text (outputs raw string)
claim_extractor_agent = LlmAgent(
    name="ClaimExtractorAgent",
    model=GEMINI_MODEL,
    instruction="""
    You are a text analysis AI. Extract all distinct, verifiable claims from the text: {{website_text}}. Try to keep the number of claims low.
    
    Return them as a JSON formatted list of strings. 
    Example: ["Claim one.", "Claim two is a fact."]
    Output *ONLY* the JSON array. DO NOT include any conversational introduction, markdown fences (```json), or closing remarks.
    """,
    output_key=STATE_RAW_CLAIMS_OUTPUT 
)

# Agent 1.5: Tool runner to parse the raw output
claims_parser_agent = SequentialAgent(
    name="ClaimsParserAgent",
    sub_agents=[
        LlmAgent(
            name="ClaimsParserToolRunner",
            model=GEMINI_MODEL,
            instruction="""
            Call the `parse_raw_claims` function to process the claims and update the state.
            """,
            tools=[parse_claims_tool]
        )
    ]
)


# --- Agents Inside the Loop ---

# Agent 2a (in loop): Decides if the loop should continue or finish
loop_controller_agent = LlmAgent(
    name="LoopControllerAgent",
    model=GEMINI_MODEL,
    instruction="""
    Your task is to determine the next step. Call the `process_next_claim` function.
    """,
    tools=[process_next_claim_tool],
    output_key=STATE_LOOP_STATUS
)

# Agent 2b (in loop): Exits the loop if the status is "finished"
exit_decision_agent = LlmAgent(
    name="ExitDecisionAgent",
    model=GEMINI_MODEL,
    instruction="""
    Read the loop status: {{loop_status}}
    If the status is exactly `{'status': 'finished'}`, you MUST call the `exit_loop` function.
    Otherwise, do nothing and output no text.
    """,
    tools=[exit_loop_tool]
)

# NEW UNIFIED AGENT: Combines Evaluator, Scorer, and Aggregator into one LLM call (FIX for rate limiting)
unified_evaluator_agent = LlmAgent(
    name="UnifiedEvaluatorAgent",
    model=GEMINI_MODEL,
    instruction="""
    Analyze the credibility of this single claim:
    Claim: {{current_claim}}
    
    1. Provide a one or two-sentence analysis covering potential bias, factual accuracy, and verifiability.
    2. Assign a credibility score from 0 to 100 based on your analysis.
    3. You MUST then call the `append_result_to_state` function with:
       - `claim`: The original claim text.
       - `analysis`: Your one or two-sentence analysis.
       - `score`: The credibility score (the number only).
    """,
    tools=[append_result_tool]
)


# Agent 2: The LoopAgent with manual control
credibility_loop = LoopAgent(
    name="ClaimAnalysisLoop",
    sub_agents=[
        loop_controller_agent,
        exit_decision_agent,
        unified_evaluator_agent,
    ],
    max_iterations=10 
)

# Agent 3: Final scoring
final_scoring_agent = LlmAgent(
    name="FinalScoringAgent",
    model=GEMINI_MODEL,
    instruction="""
    You will receive a JSON list of claim-by-claim credibility analyses.
    Results: {{aggregated_results}}
    
    Review all the results and perform two tasks:
    1.  Write a brief, final summary of the overall credibility of the source text.
    2.  Calculate an average of all the individual scores to create a final, overall score.
    
    You MUST respond with a valid JSON object containing two keys: "final_summary" and "final_score".
    Do not add any other text or markdown formatting.
    Example of the required output: {"final_summary": "A mix of verifiable and unsourced claims.", "final_score": 75}
    """
)

# Root Agent: The overall sequence
root_agent = SequentialAgent(
    name="IterativeCredibilityPipeline",
    sub_agents=[
        claim_extractor_agent,
        claims_parser_agent, 
        credibility_loop,
        final_scoring_agent
    ],
    description="Extracts claims, analyzes each in a loop, then provides a final score."
)