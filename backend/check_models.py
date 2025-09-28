import os
from dotenv import load_dotenv
import google.generativeai as genai

print("--- Starting Model Check ---")

try:
    # Load environment variables
    load_dotenv()
    if 'GEMINI_API_KEY' not in os.environ and 'GOOGLE_API_KEY' in os.environ:
        os.environ['GEMINI_API_KEY'] = os.environ['GOOGLE_API_KEY']

    if 'GEMINI_API_KEY' not in os.environ:
        raise ValueError("GEMINI_API_KEY is missing. Check your .env file.")

    # Configure the client
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    print("API Key configured. Listing models that support 'generateContent':\n")

    # List models
    found_models = False
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
            found_models = True

    if not found_models:
        print("\nNo models found that support 'generateContent'. Check your API key and access.")

except Exception as e:
    print("\n--- ERROR OCCURRED ---")
    print(f"Error Type: {type(e).__name__}")
    print(f"Details: {e}")

print("\n--- Model Check Complete ---")