import os
from pathlib import Path
from dotenv import load_dotenv

# Build a path to the root directory (one level up from backend/)
env_path = Path(__file__).resolve().parent.parent / '.env'

# Load the .env file
load_dotenv(dotenv_path=env_path)

# Export variables for your app to use
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
AI_MODEL_API_KEY = os.getenv("AI_MODEL_API_KEY")