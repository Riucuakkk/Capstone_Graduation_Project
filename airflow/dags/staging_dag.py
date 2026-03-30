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
    dag_id="staging_pipeline",
    default_args=default_args,
    schedule_interval="0 2 * * *",
    catchup=False,
) as dag:

    dbt_staging = BashOperator(
        task_id="run_dbt_staging",
        bash_command="""
        cd /opt/airflow/dbt &&
        dbt run --select path:models/staging
        """,
    )

    build_as_of_date = BashOperator(
        task_id="build_as_of_date_table",
        bash_command="""
        cd /opt/airflow/dbt &&
        dbt run --select as_of_date
        """
    )

    notify_success = build_notify_task(
        task_id="notify_staging_success",
        subject="[Airflow] staging_pipeline success",
        html_content="""
        <p>DAG <b>staging_pipeline</b> da chay thanh cong.</p>
        <p>Thoi gian xu ly: {{ ds }}.</p>
        """,
    )

    dbt_staging >> build_as_of_date >> notify_success
