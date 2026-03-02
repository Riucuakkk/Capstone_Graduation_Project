import pandas as pd
from src.utils.db_connection import get_connection


def log_result(check_name, table_name, failed_rows, status):
    conn = get_connection()
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO mart.data_quality_report
        (check_name, table_name, failed_rows, status)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(insert_query, (check_name, table_name, failed_rows, status))
    conn.commit()
    cursor.close()
    conn.close()


def check_null_primary_key(table, column):
    conn = get_connection()
    query = f"""
        SELECT COUNT(*) 
        FROM raw.{table}
        WHERE {column} IS NULL
    """
    failed = pd.read_sql(query, conn).iloc[0, 0]
    conn.close()

    status = "PASS" if failed == 0 else "FAIL"
    log_result("null_check", table, failed, status)

    if failed > 0:
        raise Exception(f"Null values found in {table}.{column}")


def check_duplicate_key(table, column):
    conn = get_connection()
    query = f"""
        SELECT COUNT(*)
        FROM (
            SELECT {column}, COUNT(*)
            FROM raw.{table}
            GROUP BY {column}
            HAVING COUNT(*) > 1
        ) t
    """
    failed = pd.read_sql(query, conn).iloc[0, 0]
    conn.close()

    status = "PASS" if failed == 0 else "FAIL"
    log_result("duplicate_check", table, failed, status)

    if failed > 0:
        raise Exception(f"Duplicate keys found in {table}.{column}")


def check_negative_price():
    conn = get_connection()
    query = """
        SELECT COUNT(*)
        FROM raw.olist_order_items_dataset
        WHERE price < 0
    """
    failed = pd.read_sql(query, conn).iloc[0, 0]
    conn.close()

    status = "PASS" if failed == 0 else "FAIL"
    log_result("negative_price_check", "olist_order_items_dataset", failed, status)

    if failed > 0:
        raise Exception("Negative price detected in raw layer")


def run_all_raw_checks():
    check_null_primary_key("olist_orders_dataset", "order_id")
    check_duplicate_key("olist_orders_dataset", "order_id")
    check_negative_price()