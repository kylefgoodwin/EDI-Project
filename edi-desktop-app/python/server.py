import sys
import json
import edi_engine  # Your library

def main():
    """
    Reads a JSON payload from stdin, parses the EDI, and prints JSON to stdout.
    This is how Electron talks to Python.
    """
    # 1. Read input from Electron
    input_data = sys.stdin.read()
    
    if not input_data:
        return

    try:
        request = json.loads(input_data)
        edi_content = request.get("content", "")
        
        # 2. Run the Parser
        result = edi_engine.parse_edi(edi_content)
        
        # 3. Print the result (Electron captures this)
        print(json.dumps(result))
        
    except Exception as e:
        # Return errors as JSON too
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()