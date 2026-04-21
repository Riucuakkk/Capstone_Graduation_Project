from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule


default_args = {
    "owner": "hopnh",
    "start_date": datetime(2024, 1, 1),
    "email": ["haohopnguyen@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

DBT_PROJECT_DIR = "/opt/airflow/dbt"


def build_dbt_task(task_id: str, model_name: str) -> BashOperator:
    return BashOperator(
        task_id=task_id,
        bash_command=f"""
        cd {DBT_PROJECT_DIR} &&
        dbt run --select {model_name}
        """,
    )


def build_notify_task(task_id: str, subject: str, html_content: str, trigger_rule: str):
    if os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true":
        return EmailOperator(
            task_id=task_id,
            to="haohopnguyen@gmail.com",
            subject=subject,
            html_content=html_content,
            trigger_rule=trigger_rule,
        )

    return EmptyOperator(task_id=task_id, trigger_rule=trigger_rule)


with DAG(
    dag_id="mart_pipeline",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    description="Run marts layer manually after vault_pipeline completes.",
) as dag:
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    notify_success = build_notify_task(
        task_id="notify_mart_success",
        subject="[Airflow] mart_pipeline success",
        html_content="""
        <p>DAG <b>mart_pipeline</b> da chay thanh cong.</p>
        <p>Thoi gian xu ly: {{ ds }}.</p>
        """,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    notify_failure = build_notify_task(
        task_id="notify_mart_failure",
        subject="[Airflow] mart_pipeline failed",
        html_content="""
        <p>DAG <b>mart_pipeline</b> da that bai.</p>
        <p>Thoi gian xu ly: {{ ds }}.</p>
        <p>Vui long kiem tra log tren Airflow.</p>
        """,
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    dim_date = build_dbt_task("run_dim_date", "dim_date")
    dim_customers = build_dbt_task("run_dim_customers", "dim_customers")
    dim_products = build_dbt_task("run_dim_products", "dim_products")
    dim_sellers = build_dbt_task("run_dim_sellers", "dim_sellers")
    dim_geography = build_dbt_task("run_dim_geography", "dim_geography")
    dim_product_category = build_dbt_task("run_dim_product_category", "dim_product_category")
    dim_payment_type = build_dbt_task("run_dim_payment_type", "dim_payment_type")
    dim_order_status = build_dbt_task("run_dim_order_status", "dim_order_status")

    fact_orders = build_dbt_task("run_fact_orders", "fact_orders")
    fact_order_items = build_dbt_task("run_fact_order_items", "fact_order_items")
    fact_payments = build_dbt_task("run_fact_payments", "fact_payments")
    fact_reviews = build_dbt_task("run_fact_reviews", "fact_reviews")

    fact_customer_orders = build_dbt_task("run_fact_customer_orders", "fact_customer_orders")
    fact_customer_monthly = build_dbt_task("run_fact_customer_monthly", "fact_customer_monthly")
    fact_seller_daily = build_dbt_task("run_fact_seller_daily", "fact_seller_daily")
    fact_product_daily = build_dbt_task("run_fact_product_daily", "fact_product_daily")
    fact_category_daily = build_dbt_task("run_fact_category_daily", "fact_category_daily")
    fact_geo_daily = build_dbt_task("run_fact_geo_daily", "fact_geo_daily")

    fact_customer_snapshot = build_dbt_task("run_fact_customer_snapshot", "fact_customer_snapshot")
    fact_order_snapshot_ml = build_dbt_task("run_fact_order_snapshot_ml", "fact_order_snapshot_ml")
    fact_delivery_line_snapshot = build_dbt_task(
        "run_fact_delivery_line_snapshot", "fact_delivery_line_snapshot"
    )
    fact_demand_series = build_dbt_task("run_fact_demand_series", "fact_demand_series")

    fact_order_predictions = build_dbt_task("run_fact_order_predictions", "fact_order_predictions")
    fact_customer_predictions = build_dbt_task(
        "run_fact_customer_predictions", "fact_customer_predictions"
    )
    fact_seller_predictions = build_dbt_task("run_fact_seller_predictions", "fact_seller_predictions")

    start >> [
        dim_date,
        dim_customers,
        dim_products,
        dim_sellers,
        dim_geography,
        dim_product_category,
        dim_payment_type,
        dim_order_status,
    ]

    [
        dim_customers,
        dim_payment_type,
        dim_order_status,
    ] >> fact_orders

    [dim_products, dim_sellers] >> fact_order_items
    dim_payment_type >> fact_payments

    [dim_customers] >> fact_reviews

    fact_orders >> fact_customer_orders
    fact_customer_orders >> [fact_customer_monthly, fact_customer_snapshot]

    fact_orders >> fact_order_snapshot_ml
    fact_order_items >> fact_delivery_line_snapshot

    fact_order_items >> [fact_seller_daily, fact_product_daily, fact_category_daily]
    fact_orders >> fact_geo_daily

    [fact_category_daily, fact_seller_daily, fact_geo_daily] >> fact_demand_series

    prediction_upstream_tasks = [fact_orders, fact_customer_snapshot, fact_seller_daily]
    prediction_tasks = [
        fact_order_predictions,
        fact_customer_predictions,
        fact_seller_predictions,
    ]

    for upstream_task in prediction_upstream_tasks:
        upstream_task >> prediction_tasks

    [
        fact_payments,
        fact_reviews,
        fact_customer_monthly,
        fact_order_snapshot_ml,
        fact_delivery_line_snapshot,
        fact_demand_series,
        fact_order_predictions,
        fact_customer_predictions,
        fact_seller_predictions,
    ] >> end

    [
        dim_date,
        dim_customers,
        dim_products,
        dim_sellers,
        dim_geography,
        dim_product_category,
        dim_payment_type,
        dim_order_status,
        fact_orders,
        fact_order_items,
        fact_payments,
        fact_reviews,
        fact_customer_orders,
        fact_customer_monthly,
        fact_seller_daily,
        fact_product_daily,
        fact_category_daily,
        fact_geo_daily,
        fact_customer_snapshot,
        fact_order_snapshot_ml,
        fact_delivery_line_snapshot,
        fact_demand_series,
        fact_order_predictions,
        fact_customer_predictions,
        fact_seller_predictions,
    ] >> notify_failure

    end >> notify_success
