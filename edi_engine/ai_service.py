import os
import json
import warnings
from typing import Optional

# Try the new google-genai package first, fallback to the old deprecated package.
_HAS_GENAI_NEW = False
_HAS_GENAI_OLD = False
genai = None

try:
    import google.genai as genai  # type: ignore
    _HAS_GENAI_NEW = True
except Exception:
    # suppress the old-package FutureWarning when importing fallback
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        try:
            import google.generativeai as genai  # type: ignore
            _HAS_GENAI_OLD = True
        except Exception:
            genai = None

# Read API key from environment — do NOT commit keys into source
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""

# Configure the old package if present (the new package uses a different client surface)
if _HAS_GENAI_OLD and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception:
        # non-fatal, we'll handle errors at call time
        pass

from . import parse_edi


def analyze_edi_with_ai(raw_edi_content: str) -> dict:
    """
    Parse the provided EDI content and (optionally) call the GenAI service.
    Behavior:
    - If `google.genai` (new) is installed, return a migration note to avoid runtime errors until the
      client code is updated to the new SDK surface.
    - If only `google.generativeai` (deprecated) is present and GEMINI_API_KEY is set, use it.
    - Otherwise return a simulated AI response so local testing is safe.
    """
    try:
        parsed = parse_edi(raw_edi_content)
    except Exception as e:
        return {"error": "Parser failure", "details": str(e)}

    if not parsed or not parsed.get("success"):
        return {"error": "Could not parse EDI, AI analysis skipped", "parsed": parsed}

    json_str = json.dumps(parsed.get("data", parsed), indent=2)

    prompt = (
        "You are an expert Supply Chain EDI analyst. Analyze the parsed EDI JSON and provide:\n"
        "1) Short human-readable summary\n"
        "2) Key fields (sender, receiver, transaction set id, counts)\n"
        "3) Any obvious data quality issues\n"
        "Return output as HTML.\n\nDATA:\n" + json_str
    )

    # If new package is installed, do not attempt to call it automatically here.
    # This prevents runtime failures until code is migrated to the new SDK surface.
    if _HAS_GENAI_NEW:
        return {
            "parsed": parsed,
            "ai_analysis": (
                "<b>GenAI available (google-genai)</b>: Please migrate edi_engine.ai_service to use the "
                "google.genai client API. AI calls are skipped to avoid runtime errors."
            ),
        }

    # Use deprecated package if available and API key is set
    if _HAS_GENAI_OLD and GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            if hasattr(response, "text"):
                text = response.text
            elif isinstance(response, dict):
                text = response.get("output", str(response))
            else:
                text = str(response)
            return {"parsed": parsed, "ai_analysis": text}
        except Exception as e:
            return {"parsed": parsed, "ai_analysis": f"AI error: {e}"}

    # No usable client/key -> simulated response
    return {
        "parsed": parsed,
        "ai_analysis": "<b>Simulated AI Response:</b> GEMINI_API_KEY not configured or SDK unavailable."
    }
