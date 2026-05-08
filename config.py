import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

MONGODB_URI = st.secrets.get("MONGODB_URI") or os.getenv("MONGODB_URI")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

MONGODB_DB = st.secrets.get("MONGODB_DB", "vynnotes") 
MONGODB_TLS_ALLOW_INVALID_CERTS = st.secrets.get("MONGODB_TLS_ALLOW_INVALID_CERTS", "false").lower() in ("1", "true", "yes")
MONGODB_NOTES_COLLECTION = st.secrets.get("MONGODB_NOTES_COLLECTION", "notes")
MONGODB_CHATS_COLLECTION = st.secrets.get("MONGODB_CHATS_COLLECTION", "chats")
