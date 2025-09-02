import sqlite3
from datetime import datetime
from typing import Optional
import hashlib
import os
import base64
import hmac

try:
    from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore
except Exception:  # pragma: no cover - fallback if werkzeug is unavailable

    def _pbkdf2_hash(password: str, salt: bytes, iterations: int = 260000) -> str:
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return base64.b64encode(dk).decode("ascii")

    def generate_password_hash(password: str) -> str:
        iterations = 260000
        salt = os.urandom(16)
        salt_b64 = base64.b64encode(salt).decode("ascii")
        h = _pbkdf2_hash(password, salt, iterations)
        return f"pbkdf2:sha256:{iterations}${salt_b64}${h}"

    def check_password_hash(pwhash: str, password: str) -> bool:
        try:
            prefix, rest = pwhash.split(":sha256:")
            iterations_s, tail = rest.split("$", 1)
            salt_b64, stored = tail.split("$", 1)
            iterations = int(iterations_s)
            salt = base64.b64decode(salt_b64)
            calc = _pbkdf2_hash(password, salt, iterations)
            return hmac.compare_digest(calc, stored)
        except Exception:
            return False


def init_db(db_path: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def get_user_by_email(db_path: str, email: str) -> Optional[sqlite3.Row]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT id, name, email, password_hash, created_at FROM users WHERE email = ?",
            (email,),
        )
        return cur.fetchone()


def authenticate_user(db_path: str, email: str, password: str) -> bool:
    row = get_user_by_email(db_path, email)
    if not row:
        return False
    return check_password_hash(row["password_hash"], password)


def create_user(db_path: str, name: str, email: str, password: str) -> bool:
    password_hash = generate_password_hash(password)
    created_at = datetime.utcnow().isoformat()
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (name, email, password_hash, created_at),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Email already exists
        return False
