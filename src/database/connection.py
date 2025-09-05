import sqlite3 as sql
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.environ.get("DATABASE_PATH") or ".data/auth.db"


def get_db_connection():
    conn = sql.connect(DATABASE_PATH)
    conn.row_factory = sql.Row
    return conn
