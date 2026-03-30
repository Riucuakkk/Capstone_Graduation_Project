from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime
import os

default_args = {
    "owner": "hopnh",
    "start_date": datetime(2024, 1, 1),
    "email": ["haohopnguyen@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
}


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
    dag_id="ingest_pipeline",
    default_args=default_args,
    schedule_interval="0 2 * * *",
    catchup=False,
    description="Init DB and ingest source data",
) as dag:

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
    )

    init_db >> ingest_data >> notify_success
