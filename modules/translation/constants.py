import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Access the configuration constants
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = os.getenv("MODEL_ID")
