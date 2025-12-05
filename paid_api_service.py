from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import uvicorn
import os
import sys

# Import your engine logic
# In the final zip, ensure 'edi_engine' folder is included
try:
    from edi_engine.ai_service import analyze_edi_with_ai
except ImportError:
    # Fallback for when running in a standalone folder structure
    sys.path.append(os.path.dirname(__file__))
    from edi_engine.ai_service import analyze_edi_with_ai

app = FastAPI(title="EDI Pro Engine (Self-Hosted)")

# --- CONFIGURATION ---
# The installer script will generate a .env file with these values
SECRET_ACCESS_TOKEN = os.getenv("EDI_SERVER_TOKEN", "change_me_please")

class EDIRequest(BaseModel):
    edi_content: str

async def verify_token(x_access_token: str = Header(...)):
    if x_access_token != SECRET_ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid Access Token")

@app.get("/")
def health_check():
    return {"status": "online", "version": "1.0.0 (Pro)"}

@app.post("/analyze", dependencies=[Depends(verify_token)])
async def analyze_endpoint(request: EDIRequest):
    """
    Unlimited AI Analysis endpoint.
    """
    try:
        # The engine automatically picks up the GEMINI_API_KEY from os.environ
        result = analyze_edi_with_ai(request.edi_content)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Standard port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)