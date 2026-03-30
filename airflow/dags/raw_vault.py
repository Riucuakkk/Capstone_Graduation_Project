from datetime import datetime
import os

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.operators.empty import EmptyOperator


default_args = {
    "owner": "hopnh",
    "start_date": datetime(2024, 1, 1),
    "email": ["haohopnguyen@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
}


def build_dbt_task(task_id: str, model_name: str) -> BashOperator:
    return BashOperator(
        task_id=task_id,
        bash_command=f"""
        cd /opt/airflow/dbt &&
        dbt run --select {model_name}
        """,
    )


def build_notify_task(task_id: str, subject: str, html_content: str):
    if os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true":
        return EmailOperator(
            task_id=task_id,
            to="haohopnguyen@gmail.com",
            subject=subject,
            html_content=html_content,
        )

    return EmptyOperator(task_id=task_id)


with DAG(
    dag_id="raw_vault_pipeline",
    default_args=default_args,
    schedule_interval="0 2 * * *",
    catchup=False,
    description="Run raw vault models with hub-link-satellite dependencies",
) as dag:
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")
    notify_success = build_notify_task(
        task_id="notify_raw_vault_success",
        subject="[Airflow] raw_vault_pipeline success",
        html_content="""
        <p>DAG <b>raw_vault_pipeline</b> da chay thanh cong.</p>
        <p>Thoi gian xu ly: {{ ds }}.</p>
        """,
    )

    hub_customer = build_dbt_task("run_hub_customer", "hub_customer")
    hub_order = build_dbt_task("run_hub_order", "hub_order")
    hub_product = build_dbt_task("run_hub_product", "hub_product")
    hub_seller = build_dbt_task("run_hub_seller", "hub_seller")
    hub_review = build_dbt_task("run_hub_review", "hub_review")

    lnk_order_customer = build_dbt_task(
        "run_lnk_order_customer", "lnk_order_customer"
    )
    lnk_order_product_seller = build_dbt_task(
        "run_lnk_order_product_seller", "lnk_order_product_seller"
    )
    lnk_order_payment = build_dbt_task("run_lnk_order_payment", "lnk_order_payment")
    lnk_order_review = build_dbt_task("run_lnk_order_review", "lnk_order_review")

    sat_customer_address = build_dbt_task(
        "run_sat_customer_address", "sat_customer_address"
    )
    sat_customer_identity = build_dbt_task(
        "run_sat_customer_identity", "sat_customer_identity"
    )
    sat_order_item_details = build_dbt_task(
        "run_sat_order_item_details", "sat_order_item_details"
    )
    sat_order_payment_details = build_dbt_task(
        "run_sat_order_payment_details", "sat_order_payment_details"
    )
    sat_order_status = build_dbt_task("run_sat_order_status", "sat_order_status")
    sat_order_timestamps = build_dbt_task(
        "run_sat_order_timestamps", "sat_order_timestamps"
    )
    sat_product_details = build_dbt_task(
        "run_sat_product_details", "sat_product_details"
    )
    sat_review_details = build_dbt_task("run_sat_review_details", "sat_review_details")
    sat_seller_address = build_dbt_task("run_sat_seller_address", "sat_seller_address")

    start >> [hub_customer, hub_order, hub_product, hub_seller, hub_review]

    [hub_order, hub_customer] >> lnk_order_customer
    [hub_order, hub_product, hub_seller] >> lnk_order_product_seller
    hub_order >> lnk_order_payment
    [hub_order, hub_review] >> lnk_order_review

    hub_customer >> [sat_customer_address, sat_customer_identity]
    hub_order >> [sat_order_status, sat_order_timestamps]
    hub_product >> sat_product_details
    hub_review >> sat_review_details
    hub_seller >> sat_seller_address
    lnk_order_product_seller >> sat_order_item_details
    lnk_order_payment >> sat_order_payment_details

    [
        lnk_order_customer,
        lnk_order_product_seller,
        lnk_order_payment,
        lnk_order_review,
        sat_customer_address,
        sat_customer_identity,
        sat_order_item_details,
        sat_order_payment_details,
        sat_order_status,
        sat_order_timestamps,
        sat_product_details,
        sat_review_details,
        sat_seller_address,
    ] >> end

    end >> notify_success
