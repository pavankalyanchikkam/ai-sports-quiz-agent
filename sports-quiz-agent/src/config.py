import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Centralized configurations
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("[WARNING]: API Key is missing. Check your .env file setup!")
