import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "src" / "schema.sql"
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "data" / "chat.db"


def connect_database(
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> sqlite3.Connection:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with connect_database(database_path) as connection:
        connection.executescript(schema)

def create_conversation(conn,title):
    cursor = conn.execute(
        'INSERT INTO conversations(title) VALUES (?)',
        (title,)
    )

    conn.commit()

    return cursor.lastrowid

def list_conversations(conn):
    cursor = conn.execute(
        'SELECT id,title FROM conversations ORDER BY id ASC'
    )

    return cursor.fetchall()

def get_conversation(conn,conversation_id):
    cursor = conn.execute(
        'SELECT id,title FROM conversations WHERE id = ?',
        (conversation_id,)
    )

    return cursor.fetchone()

def rename_conversation(conn, conversation_id, new_title):
    conn.execute(
        'UPDATE conversations SET title = ? WHERE id = ?',
        (new_title, conversation_id)
    )

    conn.commit()

def create_message(conn, conversation_id, role, content):
    conn.execute(
        'INSERT INTO messages(conversation_id,role,content) VALUES (?,?,?)',
        (conversation_id,role,content)
    )

    conn.commit()

def list_messages(conn, conversation_id):
    cursor = conn.execute(
        'SELECT id,role,content FROM messages WHERE conversation_id = ? ORDER BY id ASC',
        (conversation_id,)
    )

    return cursor.fetchall()

def update_message_content(conn, message_id, new_content):
    conn.execute(
        'UPDATE messages SET content = ? WHERE id = ?',
        (new_content,message_id)
    )

    conn.commit()

def delete_message(conn, message_id):
    conn.execute(
        'DELETE FROM messages WHERE id = ?',
        (message_id,)
    )

    conn.commit()


def delete_conversation(conn, conversation_id):
    try:
        conn.execute(
            'DELETE FROM messages WHERE conversation_id = ?',
            (conversation_id,)
        )
        conn.execute(
            'DELETE FROM conversations WHERE id = ?',
            (conversation_id,)
        )

        conn.commit()

    except sqlite3.Error:
        conn.rollback()
        raise


if __name__ == "__main__":
    initialize_database()
    print(f"数据库已初始化：{DEFAULT_DATABASE_PATH}")
