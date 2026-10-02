# src/database.py
# desc: saves and loads everything in SQLite

import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / "data" / "chess_srs.db"


def connect_to_database():
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("CREATE TABLE IF NOT EXISTS studies (color TEXT PRIMARY KEY, pgn TEXT NOT NULL)")
    return connection


def save_study_pgn(color_name, pgn_text):
    connection = connect_to_database()
    with connection:
        connection.execute("INSERT OR REPLACE INTO studies (color, pgn) VALUES (?, ?)", (color_name, pgn_text))
    connection.close()


def load_saved_study_pgn(color_name):
    connection = connect_to_database()
    row = connection.execute("SELECT pgn FROM studies WHERE color = ?", (color_name,)).fetchone()
    connection.close()
    return row[0]