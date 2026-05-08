import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI must be set in the environment or .env file.")

MONGODB_DB = os.getenv("MONGODB_DB", "vynnotes")
MONGODB_NOTES_COLLECTION = os.getenv("MONGODB_NOTES_COLLECTION", "notes")
MONGODB_CHATS_COLLECTION = os.getenv("MONGODB_CHATS_COLLECTION", "chats")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
