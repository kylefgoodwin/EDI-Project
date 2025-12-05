import sys
import json
import edi_engine

# Import the new AI service safely
try:
    from edi_engine.ai_service import analyze_edi_with_ai
except ImportError:
    analyze_edi_with_ai = None

def main():
    """
    Reads a JSON payload from Electron.
    Payload format: { "command": "parse"|"analyze", "content": "ISA*00..." }
    """
    input_data = sys.stdin.read()
    if not input_data: return

    try:
        request = json.loads(input_data)
        command = request.get("command", "parse") 
        content = request.get("content", "")

        if command == "analyze":
            if analyze_edi_with_ai:
                # This returns { parsed: {...}, ai_analysis: "..." }
                result = analyze_edi_with_ai(content)
            else:
                result = {"error": "AI Service file not found."}
        else:
            # Standard Parse (Legacy behavior)
            result = edi_engine.parse_edi(content)
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()