from pymongo import MongoClient
from datetime import datetime

from config import (
    MONGODB_CHATS_COLLECTION,
    MONGODB_DB,
    MONGODB_NOTES_COLLECTION,
    MONGODB_URI,
)

class Database:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[MONGODB_DB]
        self.notes_collection = self.db[MONGODB_NOTES_COLLECTION]
        self.chat_collection = self.db[MONGODB_CHATS_COLLECTION]

    def get_all_notes(self, user_id="default"):
        notes = list(self.notes_collection.find({"user_id": user_id}))
        for note in notes:
            note.pop("_id", None)
        return notes

    def get_note_by_id(self, note_id, user_id="default"):
        note = self.notes_collection.find_one({"id": note_id, "user_id": user_id})
        if note:
            note.pop("_id", None)
        return note

    def save_note(self, note, user_id="default"):
        note.pop("_id", None)
        note["user_id"] = user_id
        note["updated"] = datetime.now()

        existing = self.notes_collection.find_one({"id": note["id"], "user_id": user_id})
        if existing:
            self.notes_collection.replace_one({"id": note["id"], "user_id": user_id}, note)
        else:
            self.notes_collection.insert_one(note)

    def delete_note(self, note_id, user_id="default"):
        self.notes_collection.delete_one({"id": note_id, "user_id": user_id})
        self.chat_collection.delete_many({"note_id": note_id, "user_id": user_id})

    def reset_db(self):
        notes_deleted = self.notes_collection.delete_many({}).deleted_count
        chats_deleted = self.chat_collection.delete_many({}).deleted_count
        return {
            "notes_deleted": notes_deleted,
            "chats_deleted": chats_deleted
        }

    def get_chat_history(self, note_id, user_id="default"):
        chat = self.chat_collection.find_one({"note_id": note_id, "user_id": user_id})
        return chat["messages"] if chat else []

    def save_chat_history(self, note_id, messages, user_id="default"):
        self.chat_collection.replace_one(
            {"note_id": note_id, "user_id": user_id},
            {"note_id": note_id, "user_id": user_id, "messages": messages},
            upsert=True
        )

db = Database()