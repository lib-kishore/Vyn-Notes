import certifi
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime

from config import (
    MONGODB_CHATS_COLLECTION,
    MONGODB_DB,
    MONGODB_NOTES_COLLECTION,
    MONGODB_TLS_ALLOW_INVALID_CERTS,
    MONGODB_URI,
)

class Database:
    def __init__(self):
        client_options = {
            "serverSelectionTimeoutMS": 10000,
        }

        if MONGODB_URI.startswith("mongodb+srv://") or "mongodb.net" in MONGODB_URI:
            client_options["tls"] = True
            client_options["tlsCAFile"] = certifi.where()
            if MONGODB_TLS_ALLOW_INVALID_CERTS:
                client_options["tlsAllowInvalidCertificates"] = True

        self.is_available = True
        self.notes_cache = []
        self.chats_cache = {}

        try:
            self.client = MongoClient(MONGODB_URI, **client_options)
            self.client.admin.command("ping")
            self.db = self.client[MONGODB_DB]
            self.notes_collection = self.db[MONGODB_NOTES_COLLECTION]
            self.chat_collection = self.db[MONGODB_CHATS_COLLECTION]
        except PyMongoError as exc:
            print(f"Warning: MongoDB unavailable, using in-memory fallback. Error: {exc}")
            self.client = None
            self.db = None
            self.notes_collection = None
            self.chat_collection = None
            self.is_available = False

    def _set_unavailable(self, error):
        if self.is_available:
            print(f"Warning: MongoDB connection lost, switching to in-memory fallback. Error: {error}")
        self.is_available = False
        self.client = None
        self.db = None
        self.notes_collection = None
        self.chat_collection = None
        self.notes_cache = []
        self.chats_cache = {}

    def get_all_notes(self, user_id="default"):
        if not self.is_available:
            return [note for note in self.notes_cache if note.get("user_id") == user_id]

        try:
            notes = list(self.notes_collection.find({"user_id": user_id}))
        except PyMongoError as exc:
            self._set_unavailable(exc)
            return [note for note in self.notes_cache if note.get("user_id") == user_id]

        for note in notes:
            note.pop("_id", None)
        self.notes_cache = notes
        return notes

    def get_note_by_id(self, note_id, user_id="default"):
        if not self.is_available:
            return next((note for note in self.notes_cache if note.get("id") == note_id and note.get("user_id") == user_id), None)

        try:
            note = self.notes_collection.find_one({"id": note_id, "user_id": user_id})
        except PyMongoError as exc:
            self._set_unavailable(exc)
            return next((note for note in self.notes_cache if note.get("id") == note_id and note.get("user_id") == user_id), None)

        if note:
            note.pop("_id", None)
        return note

    def save_note(self, note, user_id="default"):
        note.pop("_id", None)
        note["user_id"] = user_id
        note["updated"] = datetime.now()

        if not self.is_available:
            existing = next((n for n in self.notes_cache if n.get("id") == note.get("id") and n.get("user_id") == user_id), None)
            if existing:
                self.notes_cache = [n if n.get("id") != note.get("id") else note for n in self.notes_cache]
            else:
                self.notes_cache.append(note)
            return

        try:
            existing = self.notes_collection.find_one({"id": note["id"], "user_id": user_id})
            if existing:
                self.notes_collection.replace_one({"id": note["id"], "user_id": user_id}, note)
            else:
                self.notes_collection.insert_one(note)
        except PyMongoError as exc:
            self._set_unavailable(exc)
            self.save_note(note, user_id=user_id)

    def delete_note(self, note_id, user_id="default"):
        if not self.is_available:
            self.notes_cache = [note for note in self.notes_cache if not (note.get("id") == note_id and note.get("user_id") == user_id)]
            self.chats_cache.pop((note_id, user_id), None)
            return

        try:
            self.notes_collection.delete_one({"id": note_id, "user_id": user_id})
            self.chat_collection.delete_many({"note_id": note_id, "user_id": user_id})
        except PyMongoError as exc:
            self._set_unavailable(exc)
            self.delete_note(note_id, user_id=user_id)

    def reset_db(self):
        if not self.is_available:
            self.notes_cache = []
            self.chats_cache = {}
            return {
                "notes_deleted": 0,
                "chats_deleted": 0
            }

        try:
            notes_deleted = self.notes_collection.delete_many({}).deleted_count
            chats_deleted = self.chat_collection.delete_many({}).deleted_count
            return {
                "notes_deleted": notes_deleted,
                "chats_deleted": chats_deleted
            }
        except PyMongoError as exc:
            self._set_unavailable(exc)
            return self.reset_db()

    def get_chat_history(self, note_id, user_id="default"):
        if not self.is_available:
            return self.chats_cache.get((note_id, user_id), [])

        try:
            chat = self.chat_collection.find_one({"note_id": note_id, "user_id": user_id})
        except PyMongoError as exc:
            self._set_unavailable(exc)
            return self.chats_cache.get((note_id, user_id), [])

        return chat["messages"] if chat else []

    def save_chat_history(self, note_id, messages, user_id="default"):
        if not self.is_available:
            self.chats_cache[(note_id, user_id)] = messages
            return

        try:
            self.chat_collection.replace_one(
                {"note_id": note_id, "user_id": user_id},
                {"note_id": note_id, "user_id": user_id, "messages": messages},
                upsert=True
            )
        except PyMongoError as exc:
            self._set_unavailable(exc)
            self.save_chat_history(note_id, messages, user_id=user_id)

db = Database()
