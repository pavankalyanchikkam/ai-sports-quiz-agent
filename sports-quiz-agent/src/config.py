import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Centralized configurations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("[WARNING]: API Key is missing. Check your .env file setup!")
