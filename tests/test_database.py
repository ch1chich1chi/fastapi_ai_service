import sqlite3

import pytest

from src.database import connect_database, delete_conversation, initialize_database


def test_initialize_database_creates_conversation_tables(tmp_path):
    database_path = tmp_path / "chat.db"

    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()

    table_names = {row[0] for row in rows}
    assert {"conversations", "messages"} <= table_names


def test_connection_rejects_message_for_missing_conversation(tmp_path):
    database_path = tmp_path / "chat.db"
    initialize_database(database_path)

    with connect_database(database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO messages (conversation_id, role, content)
                VALUES (?, ?, ?)
                """,
                (8, "user", "不存在的会话"),
            )

def test_delete_conversation_rolls_back_on_failure(tmp_path):
    database_path = tmp_path / "rollback.db"
    initialize_database(database_path)
    conn = connect_database(database_path)

    try:
        conn.execute(
            "INSERT INTO conversations(id, title) VALUES (?, ?)",
            (1, "回滚练习"),
        )
        conn.execute(
            """INSERT INTO messages(conversation_id, role, content)
               VALUES (?, ?, ?)""",
            (1, "user", "这条消息应该保留"),
        )
        conn.execute(
            """CREATE TABLE protected_records (
                conversation_id INTEGER REFERENCES conversations(id)
            )"""
        )
        conn.execute("INSERT INTO protected_records VALUES (?)", (1,))
        conn.commit()

        with pytest.raises(sqlite3.IntegrityError):
            delete_conversation(conn, 1)

        assert conn.execute(
            "SELECT id FROM conversations"
        ).fetchall() == [(1,)]
        assert conn.execute(
            "SELECT content FROM messages"
        ).fetchall() == [("这条消息应该保留",)]
    finally:
        conn.close()
