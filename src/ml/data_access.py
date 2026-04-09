import pandas as pd

from src.utils.db_connection import get_connection


def read_sql_frame(sql: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql(sql, conn)
    finally:
        conn.close()
