import sys
from database import db

if __name__ == "__main__":
    print("WARNING: This will permanently delete all notes and chat history from the VynNotes database.")
    confirm = input("Type RESET to continue: ")
    if confirm != "RESET":
        print("Aborted. No changes were made.")
        sys.exit(1)

    result = db.reset_db()
    print(f"Database reset complete. Deleted {result['notes_deleted']} notes and {result['chats_deleted']} chat entries.")

# just in case if needed