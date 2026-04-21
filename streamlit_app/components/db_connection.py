from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

import pandas as pd
import psycopg2
import streamlit as st


def db_config() -> dict[str, str | int]:
    """Read database settings from env so the app works locally and in Docker."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5433")),
        "database": os.getenv("DB_NAME", "ecommerce"),
        "user": os.getenv("DB_USER", "airflow"),
        "password": os.getenv("DB_PASSWORD", "airflow"),
    }


@contextmanager
def get_connection() -> Iterator:
    conn = psycopg2.connect(**db_config())
    try:
        yield conn
    finally:
        conn.close()


@st.cache_data(ttl=300, show_spinner=False)
def read_sql(sql: str, params: tuple | None = None) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=params)


def database_is_ready() -> tuple[bool, str]:
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("select 1")
                cursor.fetchone()
        return True, "Connected"
    except Exception as exc:  # pragma: no cover - shown in UI.
        return False, str(exc)
