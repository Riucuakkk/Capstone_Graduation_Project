
from __future__ import annotations

import os

import psycopg2


def db_config() -> dict[str, str | int]:
    """Read DB settings from env so ML code works locally and inside Docker."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5433")),
        "database": os.getenv("DB_NAME", "ecommerce"),
        "user": os.getenv("DB_USER", "airflow"),
        "password": os.getenv("DB_PASSWORD", "airflow"),
    }


def get_connection():
    return psycopg2.connect(**db_config())
