from fastapi import FastAPI
import os
from dotenv import load_dotenv

# 1. Load the secret vault (.env) from the folder above
load_dotenv(dotenv_path="../.env")

# 2. Get a specific secret to prove it works
supabase_url = os.getenv("SUPABASE_URL")

# 3. Initialize the FastAPI server
app = FastAPI()

# 4. Create your first endpoint (a URL route)
@app.get("/")
def read_root():
    return {
        "message": "Hello from the Python Backend!",
        "database_url_loaded": supabase_url
    }