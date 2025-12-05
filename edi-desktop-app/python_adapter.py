import sys
import json

# Because you ran 'pip install -e .', this import just works!
try:
    from edi_engine import parse_edi
except ImportError:
    # Fallback error if you forgot the pip install step
    print(json.dumps({"error": "Engine not found. Did you run 'pip install -e .' in edi-engine?"}))
    sys.exit(1)

def main():
    # Read from Electron (stdin)
    input_data = sys.stdin.read()
    
    if not input_data:
        return

    try:
        request = json.loads(input_data)
        edi_content = request.get("content", "")
        
        # RUN THE ENGINE
        result = parse_edi(edi_content)
        
        # Send back to Electron (stdout)
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()