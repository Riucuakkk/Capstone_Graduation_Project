from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime
import os

default_args = {
    "owner": "hopnh",
    "start_date": datetime(2024, 1, 1),
    "email": ["haohopnguyen@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
}


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
    dag_id="ingest_pipeline",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description="Init DB and ingest source data",
) as dag:
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    init_db = BashOperator(
        task_id="init_database",
        bash_command="""
        psql postgresql://airflow:airflow@postgres:5432/ecommerce \
        -f /opt/airflow/sql_init/create_source_tables.sql
        """
    )

    ingest_data = BashOperator(
        task_id="ingest_csv_to_postgres",
        bash_command="""
        python /opt/airflow/src/ingestion/ingest_source.py
        """
    )

    notify_success = build_notify_task(
        task_id="notify_ingest_success",
        subject="[Airflow] ingest_pipeline success",
        html_content="""
        <p>DAG <b>ingest_pipeline</b> da chay thanh cong.</p>
        <p>Thoi gian xu ly: {{ ds }}.</p>
        """,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    notify_failure = build_notify_task(
        task_id="notify_ingest_failure",
        subject="[Airflow] ingest_pipeline failed",
        html_content="""
        <p>DAG <b>ingest_pipeline</b> da that bai.</p>
        <p>Thoi gian xu ly: {{ ds }}.</p>
        <p>Vui long kiem tra log tren Airflow.</p>
        """,
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    start >> init_db >> ingest_data >> end

    [init_db, ingest_data] >> notify_failure
    end >> notify_success
