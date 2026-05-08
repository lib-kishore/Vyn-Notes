# 🧠 VynNotes

<p align="center">
  <img src="banner.png" alt="VynNotes Banner" width="100%" />
</p>

<p align="center">
  <img src="logo.png" alt="VynNotes Logo" width="120" />
</p>

<p align="center">
  <strong>Write. Think. Win.</strong>
</p>

<p align="center">
  Built by M.Kishore — a personal AI note-taking project.
</p>

---

## 🚀 Overview

**VynNotes** is a lightweight AI-powered note-taking app built with Streamlit and MongoDB.

It focuses on:
- fast note creation
- clean editing
- AI-assisted workflows
- personal productivity without unnecessary complexity

VynNotes is intentionally simple and designed for individual use.

---

## 💡 Motivation

This project was built to:
- create a clean note editor for problem solving
- learn Streamlit and Python UI development
- experiment with AI-assisted workflows
- build something practical outside the Telegram bot ecosystem

It is not intended to become a full Notion clone or enterprise workspace.

---

## 🌐 Demo

Live App: **[Vyn-Notes](https://vyn-notes.streamlit.app/)**

> Personal project — built for learning and productivity.

---

## ⚙️ Tech Stack

- **Python** — Core logic
- **Streamlit** — UI framework
- **MongoDB Atlas** — Cloud database
- **Groq API** — AI note assistance

---

## ✨ Features

- AI-assisted note editing
- Persistent MongoDB storage
- Minimal and distraction-free UI
- Instant note saving
- Recent note navigation
- Markdown downloads
- Lightweight Streamlit deployment

---

# 🚀 Local Setup

## 1. Clone Repository

```bash
git clone https://github.com/lib-kishore/Vyn-Notes.git
cd Vyn-Notes
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

## 4. Create `.env`

### Windows

```bash
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

---

## 5. Configure Environment Variables

Open `.env` and add:

```env
MONGODB_URI=your_mongodb_uri
MONGODB_DB=vynnotes
MONGODB_NOTES_COLLECTION=notes
MONGODB_CHATS_COLLECTION=chats
GROQ_API_KEY=your_groq_api_key
```

---

# ☁️ Streamlit Cloud Deployment

VynNotes now uses `st.secrets` for cloud deployment.

## Add Secrets in Streamlit Cloud

Go to:

```text
App Settings → Secrets
```

Add:

```toml
MONGODB_URI = "your_mongodb_uri"
GROQ_API_KEY = "your_groq_api_key"

MONGODB_DB = "vynnotes"
MONGODB_NOTES_COLLECTION = "notes"
MONGODB_CHATS_COLLECTION = "chats"

MONGODB_TLS_ALLOW_INVALID_CERTS = false
```

---

## 🔒 Config System

The app supports:
- local `.env` development using `python-dotenv`
- Streamlit Cloud secrets using `st.secrets`

Current configuration setup:

```python
import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

MONGODB_URI = st.secrets.get("MONGODB_URI") or os.getenv("MONGODB_URI")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

MONGODB_DB = st.secrets.get("MONGODB_DB", "vynnotes")
MONGODB_TLS_ALLOW_INVALID_CERTS = st.secrets.get(
    "MONGODB_TLS_ALLOW_INVALID_CERTS",
    "false"
).lower() in ("1", "true", "yes")

MONGODB_NOTES_COLLECTION = st.secrets.get(
    "MONGODB_NOTES_COLLECTION",
    "notes"
)

MONGODB_CHATS_COLLECTION = st.secrets.get(
    "MONGODB_CHATS_COLLECTION",
    "chats"
)
```

---

## ▶️ Run App

```bash
streamlit run note.py
```

---

## 🗑️ Reset Database

```bash
python reset_db.py
```

This removes all saved notes and chat history.

---

## ⚠️ Important Notes

- Single-user project
- No authentication system
- No multi-user support
- Minimal formatting by design
- Built for simplicity and learning

> The goal is speed and clarity, not feature overload.

---

## 🤝 Contributing

Contributions are welcome.

Please preserve the project philosophy:
- simple
- lightweight
- readable
- easy to maintain

---

## 📌 Project Status

🛠️ Personal project — actively evolving and improving.

---

## 📜 Philosophy

> Keep it simple. Keep it useful.

---

## 📬 Closing

VynNotes is not a Notion replacement.

It is a lightweight AI note-taking project built for:
- learning Streamlit
- experimenting with AI workflows
- capturing ideas quickly
- staying productive without complexity
