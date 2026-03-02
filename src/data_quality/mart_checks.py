import pandas as pd
from src.utils.db_connection import get_connection
from src.data_quality.raw_checks import log_result


def check_revenue_negative():
    conn = get_connection()
    query = """
        SELECT COUNT(*)
        FROM mart.fact_orders
        WHERE price < 0
    """
    failed = pd.read_sql(query, conn).iloc[0, 0]
    conn.close()

    status = "PASS" if failed == 0 else "FAIL"
    log_result("negative_revenue_check", "fact_orders", failed, status)

    if failed > 0:
        raise Exception("Negative revenue found in mart layer")


def check_missing_customer_fk():
    conn = get_connection()
    query = """
        SELECT COUNT(*)
        FROM mart.fact_orders f
        LEFT JOIN mart.dim_customers d
        ON f.customer_id = d.customer_id
        WHERE d.customer_id IS NULL
    """
    failed = pd.read_sql(query, conn).iloc[0, 0]
    conn.close()

    status = "PASS" if failed == 0 else "FAIL"
    log_result("fk_customer_check", "fact_orders", failed, status)

    if failed > 0:
        raise Exception("Foreign key violation: missing customer_id")


def run_all_mart_checks():
    check_revenue_negative()
    check_missing_customer_fk()