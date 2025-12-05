import os
import sys
import subprocess
import secrets
import time

def print_header():
    print("="*60)
    print("      EDI ENGINE PRO - DEPLOYMENT WIZARD      ")
    print("="*60)
    print("This script will configure your private AI Server.\n")

def check_python():
    print("[1/5] Checking System...")
    if sys.version_info < (3, 9):
        print("Error: Python 3.9+ is required.")
        sys.exit(1)
    print("Python version OK.")

def create_venv():
    print("\n[2/5] Creating Virtual Environment...")
    if not os.path.exists("venv"):
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("Virtual Environment 'venv' created.")
    else:
        print("'venv' already exists.")

def install_deps():
    print("\n[3/5] Installing Dependencies...")
    # Determine the correct pip path inside the virtual environment
    pip_cmd = os.path.join("venv", "bin", "pip") if os.name != 'nt' else os.path.join("venv", "Scripts", "pip")
    
    # These are the libraries your server needs to run
    requirements = ["fastapi", "uvicorn", "google-generativeai", "pydantic", "python-dotenv"]
    try:
        subprocess.check_call([pip_cmd, "install"] + requirements)
        print("Dependencies installed.")
    except Exception as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

def configure_secrets():
    print("\n[4/5] Configuration")
    
    # 1. Generate a secure token for their App to talk to their Server
    # This acts as the "password" between the Desktop App and the Python Script
    generated_token = secrets.token_urlsafe(16)
    
    print("To enable the AI, we need your Google Gemini API Key.")
    print("(Get one for free at https://aistudio.google.com/app/apikey)")
    api_key = input("Paste your GOOGLE_API_KEY: ").strip()
    
    # Save these to a hidden .env file
    with open(".env", "w") as f:
        f.write(f"GEMINI_API_KEY={api_key}\n")
        f.write(f"EDI_SERVER_TOKEN={generated_token}\n")
    
    print("Configuration saved to .env")
    return generated_token

def create_startup_script():
    print("\n[5/5] Finalizing...")
    
    # Create a simple "Double Click to Run" script for the user
    is_windows = os.name == 'nt'
    script_name = "start_server.bat" if is_windows else "start_server.sh"
    
    with open(script_name, "w") as f:
        if is_windows:
            f.write("@echo off\n")
            f.write("call venv\\Scripts\\activate\n")
            # The python script uses python-dotenv to load the .env file automatically
            f.write("python edi_server_pro.py\n")
            f.write("pause\n")
        else:
            f.write("#!/bin/bash\n")
            f.write("source venv/bin/activate\n")
            f.write("python edi_server_pro.py\n")
    
    if not is_windows:
        os.chmod(script_name, 0o755)
        
    print(f"Created startup script: {script_name}")
    return script_name

def main():
    print_header()
    check_python()
    create_venv()
    install_deps()
    token = configure_secrets()
    script_name = create_startup_script()
    
    print("\n" + "="*60)
    print("             INSTALLATION COMPLETE!               ")
    print("="*60)
    print("\nNext Steps:")
    print(f"1. Run './{script_name}' to start your server.")
    print("2. Open your EDI Desktop App.")
    print("3. Go to Settings -> Server Configuration.")
    print(f"4. Enter Server URL: http://localhost:8000")
    print(f"5. Enter Access Token: {token}")
    print("\nThank you for your purchase!")

if __name__ == "__main__":
    main()