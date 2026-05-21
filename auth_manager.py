import sqlite3
import hashlib
from typing import Optional

DB_FILE = "users.db"


def init_auth_db():
    """Initializes a dedicated user security database file if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            grade_level TEXT,
            learning_pace TEXT,
            strengths TEXT,
            weaknesses TEXT
        )
    ''')
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Applies a secure SHA-256 hash algorithm to user credentials."""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username: str, password: str, grade: str, pace: str, strengths: str, weaknesses: str) -> bool:
    """Registers a fresh student credentials set into the database matrix."""
    init_auth_db()
    username = username.strip().lower()
    if not username or not password:
        return False

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
            (username, hash_password(password), grade, pace, strengths, weaknesses)
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  # Username already taken
    finally:
        conn.close()
    return success


def verify_user(username: str, password: str) -> Optional[dict]:
    """Validates login attempts and fetches the matching profile dataset."""
    init_auth_db()
    username = username.strip().lower()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, grade_level, learning_pace, strengths, weaknesses FROM users WHERE username=? AND password_hash=?",
        (username, hash_password(password))
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "username": row[0],
            "grade_level": row[1],
            "learning_pace": row[2],
            "strengths": row[3],
            "weaknesses": row[4]
        }
    return None