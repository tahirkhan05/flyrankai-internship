import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Header, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase import create_client, Client

# Load environment variables from .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Initialize Supabase client
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Server running and connected to Supabase")
else:
    print("Notice: Set SUPABASE_URL and SUPABASE_KEY in .env to connect to Supabase")

app = FastAPI(title="Supabase Auth API")


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    """Ensure all auth error responses match the required JSON format: {'error': '...'}"""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


def get_current_user(authorization: Optional[str] = Header(None)):
    """Reusable auth dependency: extracts and verifies JWT bearer token with Supabase."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access token required")

    token = authorization.split("Bearer ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Access token required")

    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user_response.user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


class AuthRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


@app.get("/")
def root():
    return {
        "name": "Auth API",
        "status": "online",
        "connected_to_supabase": supabase is not None
    }


@app.post("/auth/signup", status_code=201)
def signup(credentials: AuthRequest):
    """Register a new user account with Supabase Auth."""
    if not credentials.email or not credentials.email.strip():
        return JSONResponse(status_code=400, content={"error": "Email is required"})
    if not credentials.password or not credentials.password.strip():
        return JSONResponse(status_code=400, content={"error": "Password is required"})

    try:
        response = supabase.auth.sign_up({
            "email": credentials.email.strip(),
            "password": credentials.password.strip()
        })
        if not response.user:
            return JSONResponse(status_code=400, content={"error": "Signup failed"})

        return {
            "id": response.user.id,
            "email": response.user.email,
            "created_at": str(response.user.created_at)
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.post("/auth/login")
def login(credentials: AuthRequest):
    """Authenticate credentials with Supabase Auth and return JWT tokens."""
    if not credentials.email or not credentials.email.strip():
        return JSONResponse(status_code=400, content={"error": "Email is required"})
    if not credentials.password or not credentials.password.strip():
        return JSONResponse(status_code=400, content={"error": "Password is required"})

    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email.strip(),
            "password": credentials.password.strip()
        })
        if not response.session:
            return JSONResponse(status_code=401, content={"error": "Invalid login credentials"})

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
            "expires_in": response.session.expires_in
        }
    except Exception:
        return JSONResponse(status_code=401, content={"error": "Invalid login credentials"})


@app.get("/public/info")
def public_info():
    """Public endpoint accessible to anyone without authentication."""
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile")
def profile(current_user = Depends(get_current_user)):
    """Read private profile data for the authenticated user."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": str(current_user.created_at)
    }


@app.post("/auth/logout", status_code=204)
def logout(current_user = Depends(get_current_user)):
    """End the user's session in Supabase Auth."""
    supabase.auth.sign_out()
    return Response(status_code=204)


@app.get("/protected/dashboard")
def dashboard(current_user = Depends(get_current_user)):
    """Second protected endpoint proving reusable auth middleware."""
    return {
        "message": f"Welcome to your private dashboard, {current_user.email}!",
        "user_id": current_user.id
    }

