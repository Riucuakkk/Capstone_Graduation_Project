import pandas as pd
from src.utils.db_connection import get_connection
from src.data_quality.raw_checks import log_result


def check_future_order_date():
    conn = get_connection()
    query = """
        SELECT COUNT(*)
        FROM staging.stg_orders
        WHERE order_date > CURRENT_DATE
    """
    failed = pd.read_sql(query, conn).iloc[0, 0]
    conn.close()

    status = "PASS" if failed == 0 else "FAIL"
    log_result("future_date_check", "stg_orders", failed, status)

    if failed > 0:
        raise Exception("Future order dates detected")


def check_zero_price():
    conn = get_connection()
    query = """
        SELECT COUNT(*)
        FROM staging.stg_order_items
        WHERE price <= 0
    """
    failed = pd.read_sql(query, conn).iloc[0, 0]
    conn.close()

    status = "PASS" if failed == 0 else "FAIL"
    log_result("zero_price_check", "stg_order_items", failed, status)

    if failed > 0:
        raise Exception("Zero or negative price detected in staging")


def run_all_staging_checks():
    check_future_order_date()
    check_zero_price()