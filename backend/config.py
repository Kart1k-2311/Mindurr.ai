import os
from pathlib import Path
from dotenv import load_dotenv

# Build a path to the root directory (one level up from backend/)
env_path = Path(__file__).resolve().parent.parent / '.env'

# Load the .env file
load_dotenv(dotenv_path=env_path)

# Export variables for your app to use
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
AI_API_KEY = os.getenv("AI_API_KEY")