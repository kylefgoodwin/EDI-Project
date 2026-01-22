import sys
import os
import json
import time

# 1. Setup Environment
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)

print("--- 🚀 Starting Batch AI EDI Testing ---")

# 2. Import Engine
try:
    from edi_engine.ai_service import analyze_edi_with_ai
    print("Engine loaded successfully.\n")
except ImportError:
    print("Could not load edi_engine. Make sure you are in the root folder.")
    sys.exit(1)

# 3. Define Test Cases (A mix of document types)
test_cases = [
    {
        "name": "Standard PO (850)",
        "content": """ISA*00* *00* *ZZ*SENDERID       *ZZ*RECEIVERID     *231204*1030*U*00401*000000001*0*P*>~
GS*PO*SENDERID*RECEIVERID*20231204*1030*1*X*004010~
ST*850*0001~
BEG*00*SA*PO-12345**20231204~
DTM*002*20231210~
N1*ST*SHIP TO LOCATION*92*12345~
PO1*1*100*EA*10.50**VP*PART123~
SE*8*0001~
GE*1*1~
IEA*1*000000001~"""
    },
    {
        "name": "Invoice (810) - High Value",
        "content": """ISA*00* *00* *ZZ*SUPPLIER       *ZZ*RETAILER       *231205*1400*U*00401*000000002*0*P*>~
GS*IN*SUPPLIER*RETAILER*20231205*1400*2*X*004010~
ST*810*0002~
BIG*20231205*INV-998877*20231201*PO-12345~
N1*RE*RETAILER NAME*92*STORE-001~
IT1*1*50*EA*250.00**VP*LAPTOP-X1~
TDS*1250000~
SE*6*0002~
GE*1*2~
IEA*1*000000002~"""
    },
    {
        "name": "Broken / Malformed File",
        "content": """ISA*00* ... THIS IS NOT VALID EDI ..."""
    }
]

# 4. Run Batch
results = []

for case in test_cases:
    print(f"Processing: {case['name']}...")
    
    start_time = time.time()
    
    # Call your AI Engine
    output = analyze_edi_with_ai(case['content'])
    
    duration = round(time.time() - start_time, 2)
    
    # Store result
    results.append({
        "test_name": case['name'],
        "duration_seconds": duration,
        "success": output.get("parsed", {}).get("success", False),
        "ai_summary": output.get("ai_analysis", "No Analysis"),
        "full_output": output
    })
    
    if output.get("parsed", {}).get("success", False):
        print(f"   Success ({duration}s)")
    else:
        print(f"   Failed / Skipped ({duration}s)")

# 5. Save Report
output_filename = "batch_results.json"
with open(output_filename, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n Batch complete. Results saved to: {output_filename}")
