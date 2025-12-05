import os
import json
import google.generativeai as genai
from . import parse_edi

# In production, use environment variables: os.environ["GEMINI_API_KEY"]
# For this demo, we assume the environment has the key.
api_key = "your key"
if api_key:
    genai.configure(api_key=api_key)

def analyze_edi_with_ai(raw_edi_content: str) -> dict:
    """
    1. Parses EDI deterministically (using your Python Engine).
    2. Sends the JSON to AI for business analysis.
    """
    
    # Step 1: Deterministic Parsing (The "Hard" Engine)
    parsed_result = parse_edi(raw_edi_content)
    
    if not parsed_result["success"]:
        return {"error": "Could not parse EDI, so AI analysis was skipped.", "details": parsed_result}

    # Step 2: Prepare Prompt for AI (The "Soft" Brain)
    json_str = json.dumps(parsed_result["data"], indent=2)
    
    prompt = f"""
    You are an expert Supply Chain AI Agent. 
    Analyze the following parsed EDI (Electronic Data Interchange) data.
    
    DATA:
    {json_str}
    
    YOUR TASK:
    1. Summarize: What is happening in this document in plain English?
    2. Anomalies: Are there any weird dates, missing SKUs, or urgent status codes?
    3. Action Item: What should the warehouse manager do next?
    
    Output Format: HTML (Use <b> for bold, <ul> for lists). Keep it concise.
    """

    # Step 3: Call AI
    try:
        # Check if we have a key (Mock response if not, for safety in your local testing)
        if not api_key:
            return {
                "parsed": parsed_result,
                "ai_analysis": "<b>Simulated AI Response:</b> (Add GEMINI_API_KEY to env vars to enable real AI)<br><br>This is an <b>850 Purchase Order</b> for 100 units. No anomalies detected."
            }

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        return {
            "parsed": parsed_result,
            "ai_analysis": response.text
        }
        
    except Exception as e:
        return {
            "parsed": parsed_result,
            "ai_analysis": f"AI Error: {str(e)}"
        }
