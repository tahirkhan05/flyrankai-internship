import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
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


@app.get("/")
def root():
    return {
        "name": "Auth API",
        "status": "online",
        "connected_to_supabase": supabase is not None
    }

