import os
import sqlite3
from contextlib import contextmanager


def get_db_path() -> str:
    """
    DB dosyasını proje içindeki tek bir dosyada tutar.
    Böylece kurulum/dağıtım kolay olur.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "market.db")


@contextmanager
def get_connection():
    """
    Her repository çağrısı için yeni bağlantı açar.
    SQLite küçük projelerde güvenli/kolay bir yaklaşımdır.
    """
    conn = sqlite3.connect(get_db_path())
    try:
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        conn.close()

