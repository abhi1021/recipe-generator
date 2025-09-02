import os
import sqlite3
from datetime import datetime

import pytest

import auth_service as auth


@pytest.fixture()
def temp_db(tmp_path):
    db_path = tmp_path / "test_auth.db"
    # Ensure DB is initialized
    auth.init_db(str(db_path))
    return str(db_path)


def test_init_db_creates_users_table(temp_db):
    # If init_db didn't create table, querying will fail
    with sqlite3.connect(temp_db) as conn:
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        row = cur.fetchone()
        assert row is not None
        assert row[0] == "users"


def test_create_user_success_and_row_persisted(temp_db):
    ok = auth.create_user(temp_db, name="Alice", email="alice@example.com", password="secret123")
    assert ok is True

    row = auth.get_user_by_email(temp_db, "alice@example.com")
    assert row is not None
    assert row["name"] == "Alice"
    assert row["email"] == "alice@example.com"
    # password_hash should not equal plaintext password
    assert row["password_hash"] != "secret123"
    # created_at should be ISO string parseable by datetime.fromisoformat
    datetime.fromisoformat(row["created_at"])  # will raise if invalid


def test_create_user_duplicate_email_returns_false(temp_db):
    assert auth.create_user(temp_db, "Bob", "bob@example.com", "pw1") is True
    assert auth.create_user(temp_db, "Bob Again", "bob@example.com", "pw2") is False


def test_authenticate_user_correct_and_wrong_password(temp_db):
    auth.create_user(temp_db, "Carol", "carol@example.com", "strong-pass")

    assert auth.authenticate_user(temp_db, "carol@example.com", "strong-pass") is True
    assert auth.authenticate_user(temp_db, "carol@example.com", "wrong") is False


def test_authenticate_user_nonexistent_returns_false(temp_db):
    assert auth.authenticate_user(temp_db, "nouser@example.com", "anything") is False


def test_get_user_by_email_returns_none_for_missing(temp_db):
    assert auth.get_user_by_email(temp_db, "missing@example.com") is None
