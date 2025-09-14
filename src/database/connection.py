import psycopg
from src.database.settings import settings

DATABASE_URL = f"{settings.DB_HOSTNAME}://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_TABLE}"


def get_db_connection():
    conn = psycopg.connect(DATABASE_URL)
    return conn
