import re
import uuid
import pandas as pd
import streamlit as st

from datetime import datetime

from ai import (
    vyn_chat,
    should_edit_note,
    edit_note,
    generate_title
)

from text import WELCOME_NOTE
from database import db

st.set_page_config(
    page_title="VynNotes",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "user_id" not in st.session_state:
    st.session_state.user_id = "default"

if "current_note_id" not in st.session_state:
    notes = db.get_all_notes(st.session_state.user_id)
    if not notes:
        welcome_id = str(uuid.uuid4())
        welcome_note = {
            "id": welcome_id,
            "title": "🚀 Welcome",
            "content": WELCOME_NOTE,
            "created": datetime.now(),
            "updated": datetime.now(),
            "last_viewed": datetime.now(),
            "history": [WELCOME_NOTE],
            "history_index": 0,
            "title_set_by_user": True,
            "is_welcome": True
        }
        db.save_note(welcome_note, st.session_state.user_id)
        notes = [welcome_note]
    st.session_state.current_note_id = notes[0]["id"]

if "page" not in st.session_state:
    st.session_state.page = "home"

if "preview" not in st.session_state:
    st.session_state.preview = False

if "chat" not in st.session_state:
    st.session_state.chat = {}

def format_time_ago(dt):
    diff = datetime.now() - dt
    seconds = int(diff.total_seconds())
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    if minutes < 1:
        return "Just now"
    if minutes < 60:
        return f"{minutes} min ago"
    if hours < 24:
        return f"{hours} hr ago"
    return f"{days} day ago"

def get_note_by_id(note_id):
    return db.get_note_by_id(note_id, st.session_state.user_id)

def get_current_note():
    note = get_note_by_id(st.session_state.current_note_id)
    if note:
        return note
    notes = db.get_all_notes(st.session_state.user_id)
    return notes[0] if notes else None


def sanitize_file_name(name):
    return re.sub(r"[^\w\-\s]", "", name).strip() or "note"


def create_note():
    new_id = str(uuid.uuid4())
    note = {
        "id": new_id,
        "title": "📝 Untitled",
        "content": "",
        "created": datetime.now(),
        "updated": datetime.now(),
        "last_viewed": datetime.now(),
        "history": [""],
        "history_index": 0,
        "title_set_by_user": False,
        "is_welcome": False
    }
    db.save_note(note, st.session_state.user_id)
    st.session_state.current_note_id = new_id
    st.session_state.page = "editor"
    st.session_state.preview = False

def add_history(note, text):
    if not isinstance(text, str):
        return
    current = note["history"][note["history_index"]]
    if current == text:
        return
    note["history"] = note["history"][: note["history_index"] + 1]
    note["history"].append(text)
    note["history_index"] += 1
    if len(note["history"]) > 100:
        note["history"].pop(0)
        note["history_index"] -= 1
    db.save_note(note, st.session_state.user_id)

def undo_note(note):
    if note["history_index"] > 0:
        note["history_index"] -= 1
        note["content"] = note["history"][note["history_index"]]
        editor_key = f"editor_{note['id']}"
        if editor_key in st.session_state:
            del st.session_state[editor_key]
        db.save_note(note, st.session_state.user_id)

def redo_note(note):
    if note["history_index"] < len(note["history"]) - 1:
        note["history_index"] += 1
        note["content"] = note["history"][note["history_index"]]
        editor_key = f"editor_{note['id']}"
        if editor_key in st.session_state:
            del st.session_state[editor_key]
        db.save_note(note, st.session_state.user_id)

def auto_generate_title(note):
    title = generate_title(note["content"])
    return title if title else "📝 Untitled"

def handle_vyn(line, full_note):
    return "Inline commands removed. Use the chat interface instead."

def process_note(text):
    return text

def process_vyn_blocks(text):
    return text

def text_parse(text):
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.strip() == "---":
            st.divider()
        elif line.strip().startswith("- [ ]"):
            st.checkbox(line.replace("- [ ]", "").strip(), value=False, key=f"cb_{i}")
        elif line.strip().startswith("- [x]"):
            st.checkbox(line.replace("- [x]", "").strip(), value=True, key=f"cb_{i}")
        elif line.strip().startswith("```"):
            lang = line.replace("```", "").strip()
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            st.code("\n".join(code), language=lang if lang else None)
        elif "|" in line:
            table = []
            while i < len(lines) and "|" in lines[i]:
                table.append(lines[i])
                i += 1
            try:
                cleaned = []
                for row in table:
                    row = row.strip()
                    if row.startswith("|"):
                        row = row[1:]
                    if row.endswith("|"):
                        row = row[:-1]
                    cleaned.append(row)
                headers = [h.strip() for h in cleaned[0].split("|")]
                rows = []
                for row in cleaned[2:]:
                    cols = [c.strip() for c in row.split("|")]
                    while len(cols) < len(headers):
                        cols.append("")
                    rows.append(cols[:len(headers)])
                if rows:
                    df = pd.DataFrame(rows, columns=headers)
                    df.index = df.index + 1
                    st.dataframe(df, height=200)
                else:
                    st.markdown("\n".join(table))
            except:
                st.markdown("\n".join(table))
            continue
        elif line.strip().startswith(">"):
            st.markdown(f"> {line[1:].strip()}")
        elif line.startswith("# "):
            st.title(line.replace("# ", ""))
        elif line.startswith("## "):
            st.header(line.replace("## ", ""))
        elif line.startswith("### "):
            st.subheader(line.replace("### ", ""))
        else:
            st.markdown(line)
        i += 1

logo1, logo2 = st.sidebar.columns([1, 3])

with logo1:
    st.image(
        "https://raw.githubusercontent.com/MKishoreDev/Vyn-Notes/refs/heads/main/logo.png",
        width=42
    )

with logo2:
    st.subheader("🚀 VynNotes")

search = st.sidebar.text_input(
    "Search",
    placeholder="🔍 Search Notes",
    label_visibility="collapsed"
)

if st.sidebar.button(
    "🏠 Home",
    use_container_width=True
):
    st.session_state.page = "home"
    st.rerun()

if st.sidebar.button(
    "➕ New Note",
    use_container_width=True
):
    create_note()
    st.rerun()

st.sidebar.divider()

st.sidebar.subheader("🕒 Recent")

recent_notes = sorted(
    db.get_all_notes(st.session_state.user_id),
    key=lambda x: x["last_viewed"],
    reverse=True
)

for note in recent_notes:
    if (
        search.lower() in note["title"].lower()
        or
        search.lower() in note["content"].lower()
    ):
        if st.sidebar.button(
            f"📄 {note['title']}",
            key=note["id"],
            use_container_width=True
        ):
            st.session_state.current_note_id = note["id"]
            note["last_viewed"] = datetime.now()
            st.session_state.page = "editor"
            st.session_state.preview = False
            st.rerun()

if st.session_state.page == "home":
    st.title("👋 Welcome to VynNotes")
    st.caption("Write • Think • Win")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        with st.container():
            st.subheader("📝 Notes")
            st.caption("Write and organize ideas")

    with c2:
        with st.container():
            st.subheader("✅ Tasks")
            st.caption("Manage daily workflow")

    with c3:
        with st.container():
            st.subheader("📄 Docs")
            st.caption("Create smart documents")

    with c4:
        with st.container():
            st.subheader("🤖 AI")
            st.caption("AI powered assistant")

    st.divider()

    st.subheader("🕒 Recent Notes")

    for note in recent_notes[:8]:
        with st.container():
            left, right = st.columns([7, 1])
            with left:
                if st.button(
                    f"📄 {note['title']}",
                    key=f"home_{note['id']}",
                    use_container_width=True
                ):
                    st.session_state.current_note_id = note["id"]
                    st.session_state.page = "editor"
                    note["last_viewed"] = datetime.now()
                    st.rerun()
            with right:
                st.caption(format_time_ago(note["updated"]))

else:
    note = get_current_note()
    if note is None:
        create_note()
        st.rerun()

    note["last_viewed"] = datetime.now()
    db.save_note(note, st.session_state.user_id)

    if note["id"] not in st.session_state.chat:
        st.session_state.chat[note["id"]] = db.get_chat_history(note["id"], st.session_state.user_id)

    top1, top2, top3, top4, top5, top6 = st.columns([8, 1, 1, 1, 1, 1])

    with top1:
        title = st.text_input(
            "Title",
            value=note["title"],
            placeholder="Untitled",
            label_visibility="collapsed"
        )
        if title != note["title"]:
            note["title"] = title
            note["title_set_by_user"] = True
            note["updated"] = datetime.now()
            db.save_note(note, st.session_state.user_id)

    with top2:
        preview_icon = "✍️" if st.session_state.preview else "👁️"
        if st.button(preview_icon, use_container_width=True):
            st.session_state.preview = not st.session_state.preview
            st.rerun()

    with top3:
        if st.button("↶", use_container_width=True):
            undo_note(note)
            st.rerun()

    with top4:
        if st.button("↷", use_container_width=True):
            redo_note(note)
            st.rerun()

    with top5:
        st.download_button(
            "⬇️",
            data=note["content"],
            file_name=f"{sanitize_file_name(note['title'])}.md",
            mime="text/plain",
            use_container_width=True
        )

    with top6:
        if st.button("🗑️", use_container_width=True):
            delete_id = note["id"]
            db.delete_note(delete_id, st.session_state.user_id)
            notes = db.get_all_notes(st.session_state.user_id)
            if not notes:
                create_note()
                notes = db.get_all_notes(st.session_state.user_id)
            st.session_state.current_note_id = notes[0]["id"]
            st.session_state.page = "home"
            st.rerun()

    st.caption(f"🕒 Updated {format_time_ago(note['updated'])}")

    st.divider()

    if not st.session_state.preview:
        editor_key = f"editor_{note['id']}"
        if editor_key not in st.session_state:
            st.session_state[editor_key] = note["content"]

        editor_value = st.text_area(
            "Editor",
            key=editor_key,
            height=600
        )

        if editor_value != note["content"]:
            note["content"] = editor_value
            note["updated"] = datetime.now()
            if (
                not note.get("is_welcome", False)
                and not note.get("title_set_by_user", False)
                and (note["title"] == "📝 Untitled" or note["title"].strip() == "")
            ):
                note["title"] = auto_generate_title(note)
            add_history(note, editor_value)
            db.save_note(note, st.session_state.user_id)

    else:
        text_parse(note["content"])

    st.divider()

    st.subheader("🤖 Vyn AI Assistant")

    current_chat = st.session_state.chat[note["id"]]

    chat_container = st.container()

    with chat_container:
        if not current_chat:
            st.caption("💬 Ask me anything about your notes! I can help you edit, organize, or answer questions.")
        else:
            for msg in current_chat:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

    user_msg = st.chat_input("Ask Vyn anything about your notes...")

    if user_msg:
        current_chat.append({
            "role": "user",
            "content": user_msg
        })

        db.save_chat_history(note["id"], current_chat, st.session_state.user_id)

        with st.spinner("Vyn is thinking..."):
            try:
                should_edit = should_edit_note(
                    user_msg,
                    note["content"],
                    current_chat
                )

                if should_edit:
                    with st.spinner("Updating your note..."):
                        updated_note = edit_note(
                            note["content"],
                            user_msg,
                            current_chat
                        )

                    if updated_note and updated_note != note["content"]:
                        editor_key = f"editor_{note['id']}"
                        if editor_key in st.session_state:
                            del st.session_state[editor_key]

                        note["content"] = updated_note
                        note["updated"] = datetime.now()
                        add_history(note, updated_note)

                        if not note.get("title_set_by_user", False) and not note.get("is_welcome", False):
                            new_title = generate_title(updated_note)
                            if new_title and new_title != "Untitled":
                                note["title"] = new_title

                        db.save_note(note, st.session_state.user_id)

                        response = "✅ I've updated your note! Check the changes above."
                    else:
                        response = "I couldn't make the requested changes. Could you be more specific about what you'd like me to do?"
                else:
                    response = vyn_chat(current_chat, user_msg, note["content"])

            except Exception as e:
                response = f"⚠️ Sorry, I encountered an error: {str(e)}. Please try again."

        current_chat.append({
            "role": "assistant",
            "content": response
        })

        db.save_chat_history(note["id"], current_chat, st.session_state.user_id)

        st.rerun()

st.divider()

footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col1:
    st.caption("🚀 VynNotes v1.0")

with footer_col2:
    st.caption("Built with ❤️ using Streamlit & Groq AI")

with footer_col3:
    st.caption("© 2026 VynNotes")