import os
from .config import DATA_PATH
from .db import get_connection


def file_to_table(file_name):
    """
    Convert file name -> table name
    olist_orders_dataset.csv -> source.orders
    """
    name = file_name.replace(".csv", "")
    name = name.replace("olist_", "")
    name = name.replace("_dataset", "")
    return f"source.{name}"


def ingest_file(file_path, table_name):
    conn = get_connection()
    cursor = conn.cursor()

    print(f"Loading {file_path} → {table_name}")

    try:
        cursor.execute(f"TRUNCATE TABLE {table_name};")
        with open(file_path, "r", encoding="utf-8") as f:
            cursor.copy_expert(
                f"""
                COPY {table_name}
                FROM STDIN
                WITH (
                    FORMAT CSV,
                    HEADER TRUE
                )
                """,
                f
            )
        conn.commit()
        print(f"Finished {table_name}")

    except Exception as e:
        conn.rollback()
        print(f"ERROR loading {table_name}: {e}")
    finally:
        cursor.close()
        conn.close()


def run_ingestion():
    files = sorted(os.listdir(DATA_PATH))
    for file in files:
        if file.endswith(".csv"):
            table_name = file_to_table(file)
            file_path = os.path.join(DATA_PATH, file)
            ingest_file(file_path, table_name)


if __name__ == "__main__":
    run_ingestion()