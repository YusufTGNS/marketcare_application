import os
import sqlite3
from contextlib import contextmanager


def get_db_path() -> str:
    """Veritabani dosyasinin proje icinde sabit bir konumda tutulmasini saglar."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "market.db")


@contextmanager
def get_connection():
    """Her islem icin ayri SQLite baglantisi uretir."""
    conn = sqlite3.connect(get_db_path())
    try:
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        conn.close()
