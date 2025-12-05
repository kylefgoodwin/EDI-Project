import sys
import json
import os

# 1. Setup the Environment for the Engine
# This allows us to import your existing logic without pip installing it again
sys.path.append(os.path.join(os.path.dirname(__file__), 'edi_engine'))

try:
    from edi_engine.ai_service import analyze_edi_with_ai
except ImportError:
    # Fallback if the rename didn't happen yet
    print("Error: Could not import 'ai_service'. Did you rename 'ai-service.py' to 'ai_service.py'?", file=sys.stderr)
    sys.exit(1)

def process_file(input_path, output_path):
    """
    Reads raw EDI -> Runs Parsing & AI -> Saves JSON
    """
    print(f"Processing: {input_path}...")
    
    # 1. Read Raw Input
    try:
        with open(input_path, 'r') as f:
            raw_content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {input_path}")
        return

    # 2. Run the Engine (The logic you already built)
    # This automatically detects type (850/940/etc) and asks Gemini for analysis
    result = analyze_edi_with_ai(raw_content)

    # 3. Save to JSON
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=4)
        
    print(f"Success! Output saved to: {output_path}")

if __name__ == "__main__":
    # Usage: python automation.py input.edi output.json
    if len(sys.argv) < 3:
        print("Usage: python automation.py <input_file> <output_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    process_file(input_file, output_file)