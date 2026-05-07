import os

from src.ingestion.config import DATA_PATH
from src.ingestion.db import get_connection


def file_to_table(file_name):
    """
    Convert file name -> table name.
    olist_orders_dataset.csv -> source.orders
    """
    special_mappings = {
        "olist_product_category_names_dataset.csv": "source.product_category_name_translation",
    }

    if file_name in special_mappings:
        return special_mappings[file_name]

    name = file_name.replace(".csv", "")
    name = name.replace("olist_", "")
    name = name.replace("_dataset", "")
    return f"source.{name}"


def ingest_file(file_path, table_name):
    conn = get_connection()
    cursor = conn.cursor()

    print(f"Loading {file_path} -> {table_name}")

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
                f,
            )
        conn.commit()
        print(f"Finished {table_name}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"ERROR loading {table_name}: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def run_ingestion():
    csv_files = []

    for root, _, files in os.walk(DATA_PATH):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))

    csv_files = sorted(csv_files)

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found under {DATA_PATH}")

    failed_tables = []

    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        table_name = file_to_table(file_name)
        if not ingest_file(file_path, table_name):
            failed_tables.append(table_name)

    if failed_tables:
        raise RuntimeError(
            f"Ingestion failed for {len(failed_tables)} table(s): {', '.join(failed_tables)}"
        )


if __name__ == "__main__":
    run_ingestion()
