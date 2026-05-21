import sqlite3
import hashlib
import os

DB_NAME = "users.db"


def init_auth_db():
    """Initializes the secure user identity table and runs migrations if needed."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # 1. Create the base table structure if it's a completely fresh deploy
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL DEFAULT ''
            )
        """)

        # 2. MIGRATION PATCH: If table existed from an older build without 'salt', inject it dynamically
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        if "salt" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN salt TEXT NOT NULL DEFAULT ''")

        conn.commit()


def hash_password(password: str, salt: bytes) -> str:
    """Hashes passwords securely using SHA-256 combined with a unique salt matrix."""
    return hashlib.sha256(salt + password.encode()).hexdigest()


def register_user(username: str, password: str) -> bool:
    """Registers a new student identity with an isolated cryptographic salt."""
    username = username.strip().lower()
    if not username or not password:
        return False
    try:
        salt = os.urandom(16)  # Generate 16-byte cryptographically secure salt
        p_hash = hash_password(password, salt)

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, p_hash, salt.hex())
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False  # Username already taken


def verify_user(username: str, password: str) -> bool:
    """Validates user login by verifying the salted hash map."""
    username = username.strip().lower()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            stored_hash, stored_salt = row[0], bytes.fromhex(row[1])
            return hash_password(password, stored_salt) == stored_hash
    return False