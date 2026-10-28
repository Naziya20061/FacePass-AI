import sqlite3
from pathlib import Path
import uuid

# Database file stored in the project directory
DB_PATH = Path(__file__).resolve().parent / "facepass.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS visitors (
                visitor_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                interests TEXT NOT NULL,
                photograph_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def register_visitor(name, interests, photograph_path):
    visitor_id = str(uuid.uuid4())[:8].upper()

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO visitors (
                visitor_id,
                name,
                interests,
                photograph_path
            )
            VALUES (?, ?, ?, ?)
        """, (
            visitor_id,
            name,
            ", ".join(interests),
            str(photograph_path)
        ))

    return visitor_id


def get_all_visitors():
    with get_connection() as connection:
        cursor = connection.execute("""
            SELECT visitor_id, name, interests, created_at
            FROM visitors
            ORDER BY created_at DESC
        """)

        return cursor.fetchall()


def get_visitor(visitor_id):
    with get_connection() as connection:
        cursor = connection.execute("""
            SELECT visitor_id, name, interests, photograph_path
            FROM visitors
            WHERE visitor_id = ?
        """, (visitor_id,))

        return cursor.fetchone()


# Create the database and table
initialize_database()