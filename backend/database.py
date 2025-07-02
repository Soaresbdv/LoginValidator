import sqlite3
from contextlib import closing

def init_db():
    with closing(sqlite3.connect('auth.db')) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT,
                twofa_secret TEXT,
                twofa_enabled BOOLEAN DEFAULT 0
            )
        ''')
        conn.commit()