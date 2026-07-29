"""Local-only SQLite storage and conversation privacy helpers for Cognit."""

import os
import re
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4


# Database stays as a local file on the device running Cognit.
APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("COGNIT_DATA_DIR", APP_DIR)).expanduser().resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIR / "cognit.db"

conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA foreign_keys=ON")

cursor = conn.cursor()
DB_LOCK = threading.RLock()


# Removes common personal data before conversation text is stored.
_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE = re.compile(
    r"(?<!\w)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{6,10}(?!\w)"
)
_AADHAAR = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")
_CARD = re.compile(r"\b(?:\d[ -]?){13,19}\b")
_SECRET = re.compile(
    r"\b(?:api[_ -]?key|token|password|secret)\s*[:=]\s*[^\s,;]+",
    re.IGNORECASE,
)


def redact_personal_data(text):
    """Remove direct personal details before saving a conversation."""
    if not isinstance(text, str):
        return ""

    cleaned = _EMAIL.sub("[email removed]", text)
    cleaned = _AADHAAR.sub("[ID removed]", cleaned)
    cleaned = _CARD.sub("[card number removed]", cleaned)
    cleaned = _PHONE.sub("[phone number removed]", cleaned)
    cleaned = _SECRET.sub("[secret removed]", cleaned)

    return cleaned


def new_conversation_id():
    """Create a random ID that is not linked to an account or email."""
    return uuid4().hex


def _purge_expired_conversations():
    """Automatically remove old anonymized chats after 30 days."""
    retention_days = max(
        1,
        int(os.getenv("COGNIT_CONVERSATION_RETENTION_DAYS", "30"))
    )

    cutoff = (
        datetime.now(timezone.utc) - timedelta(days=retention_days)
    ).isoformat()

    cursor.execute(
        "DELETE FROM anonymized_chats WHERE created < ?",
        (cutoff,)
    )


def save_anonymized_chat(conversation_id, role, message):
    """
    Save only redacted conversation text locally.
    No email, username, password, or account ID is stored with the chat.
    """
    if role not in {"user", "assistant"}:
        raise ValueError("Unsupported chat role")

    redacted = redact_personal_data(message)

    with DB_LOCK:
        cursor.execute(
            """
            INSERT INTO anonymized_chats
            (conversation_id, role, message, created)
            VALUES (?, ?, ?, ?)
            """,
            (
                conversation_id,
                role,
                redacted,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        _purge_expired_conversations()
        conn.commit()

    return redacted


# User accounts remain only in this local SQLite database.
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT UNIQUE,
    password TEXT,
    premium INTEGER DEFAULT 0
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS settings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    memory INTEGER DEFAULT 0,
    consent INTEGER DEFAULT 0
)
""")


# Privacy-safe conversation table.
# It intentionally has no email column.
cursor.execute("""
CREATE TABLE IF NOT EXISTS anonymized_chats(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    message TEXT NOT NULL,
    created TEXT NOT NULL
)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_anonymized_chats_created
ON anonymized_chats(created)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS library(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    description TEXT,
    price REAL,
    rent_price REAL,
    file_path TEXT
)
""")


cursor.execute("PRAGMA table_info(library)")
existing_cols = [row[1] for row in cursor.fetchall()]


def _add_column_if_missing(col_name, col_def):
    if col_name not in existing_cols:
        cursor.execute(f"ALTER TABLE library ADD COLUMN {col_def}")
        existing_cols.append(col_name)


_add_column_if_missing("description", "description TEXT")
_add_column_if_missing("price", "price REAL")
_add_column_if_missing("rent_price", "rent_price REAL")
_add_column_if_missing("file_path", "file_path TEXT")


cursor.execute("SELECT COUNT(*) FROM library")

if cursor.fetchone()[0] == 0:
    cursor.execute(
        """
        INSERT INTO library
        (title, author, description, price, rent_price, file_path)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            "Python Basics",
            "John Smith",
            "Learn Python from scratch",
            99,
            29,
            "books/python.pdf",
        ),
    )


cursor.execute("""
CREATE TABLE IF NOT EXISTS purchases(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    book_id INTEGER,
    type TEXT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


with DB_LOCK:
    _purge_expired_conversations()
    conn.commit()