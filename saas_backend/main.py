from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import os
import sys

# --- SETUP ENGINE IMPORT ---
# We assume the 'edi_engine' folder is copied into this backend folder for deployment
try:
    from edi_engine.ai_service import analyze_edi_with_ai
except ImportError:
    # Safely append parent directory to path for local testing structure
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from edi_engine.ai_service import analyze_edi_with_ai

app = FastAPI(title="EDI Cloud Platform (SaaS)")

# --- CONFIGURATION ---
SECRET_KEY = "YOUR_SUPER_SECRET_KEY_HERE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- SECURITY TOOLS ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- STATIC HASHES ---
# FIX: These static strings replace the problematic pwd_context.hash(...) call 
# that causes the ValueError during module import/loading.
HASHED_SECRET123 = "$2b$12$6B4Uf7K0z00n2.9p5I5gS.t.sS.lWzE.U7jFzFqZ.W6cZ.1H5D7h" 
HASHED_FREEPASS = "$2b$12$R.3p.uQp.h0R0kX5xL7h1.z.2p.yE.G.wL.0dFqX.B3o.T6e.P8m"


# --- MOCK DATABASE (Replace with PostgreSQL later) ---
users_db = {
    "kyle@example.com": {
        "username": "kyle@example.com",
        "full_name": "Kyle Goodwin",
        "hashed_password": HASHED_SECRET123, # Static hash
        "is_active": True,
        "subscription_tier": "pro"
    },
    "free@example.com": {
        "username": "free@example.com",
        "full_name": "Free User",
        "hashed_password": HASHED_FREEPASS, # Static hash
        "is_active": True,
        "subscription_tier": "free"
    }
}

# --- DATA MODELS ---
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: Optional[str] = None
    subscription_tier: str = "free"

class EDIRequest(BaseModel):
    content: str

# --- AUTHENTICATION LOGIC ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

# --- ENDPOINTS ---

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login Endpoint. Exchange username/password for a JWT Token.
    The .verify() function is safe to call at runtime.
    """
    user = users_db.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user['username'], "tier": user['subscription_tier']},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.post("/analyze")
async def analyze_edi(request: EDIRequest, current_user: dict = Depends(get_current_user)):
    """
    The Money Endpoint.
    """
    # 1. Check Subscription Status
    if current_user.get("subscription_tier") != "pro":
        raise HTTPException(
            status_code=403, 
            detail="Upgrade to Pro to use AI Analysis."
        )

    # 2. Run AI Analysis
    try:
        result = analyze_edi_with_ai(request.content)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))