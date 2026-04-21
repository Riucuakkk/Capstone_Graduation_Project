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
    dag_id="staging_pipeline",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    dbt_staging = BashOperator(
        task_id="run_dbt_staging",
        bash_command="""
        cd /opt/airflow/dbt &&
        dbt run --select path:models/staging
        """,
    )

    notify_success = build_notify_task(
        task_id="notify_staging_success",
        subject="[Airflow] staging_pipeline success",
        html_content="""
        <p>DAG <b>staging_pipeline</b> da chay thanh cong.</p>
        <p>Thoi gian xu ly: {{ ds }}.</p>
        """,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    notify_failure = build_notify_task(
        task_id="notify_staging_failure",
        subject="[Airflow] staging_pipeline failed",
        html_content="""
        <p>DAG <b>staging_pipeline</b> da that bai.</p>
        <p>Thoi gian xu ly: {{ ds }}.</p>
        <p>Vui long kiem tra log tren Airflow.</p>
        """,
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    start >> dbt_staging >> end

    dbt_staging >> notify_failure
    end >> notify_success
