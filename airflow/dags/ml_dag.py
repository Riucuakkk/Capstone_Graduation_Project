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

PROJECT_DIR = "/opt/airflow"
ML_TASKS = [
    "product_bestseller",
    "order_success",
    "geo_high_demand",
]


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


def build_train_task(task_name: str) -> BashOperator:
    return BashOperator(
        task_id=f"train_{task_name}",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        python -m src.ml.train_model \
          --task {task_name} \
          --persist-run \
          --run-id "{task_name}::train::{{{{ run_id }}}}"
        """,
    )


def build_predict_task(task_name: str) -> BashOperator:
    return BashOperator(
        task_id=f"predict_{task_name}",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        python -m src.ml.predict \
          --task {task_name} \
          --limit 0 \
          --write-output \
          --run-id "{task_name}::predict::{{{{ run_id }}}}" \
          --source-run-id "{task_name}::train::{{{{ run_id }}}}"
        """,
    )


with DAG(
    dag_id="ml_pipeline",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    description="Train ML artifacts and write batch predictions after mart_pipeline completes.",
) as dag:
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    notify_success = build_notify_task(
        task_id="notify_ml_success",
        subject="[Airflow] ml_pipeline success",
        html_content="""
        <p>DAG <b>ml_pipeline</b> da chay thanh cong.</p>
        <p>Thoi gian xu ly: {{ ds }}.</p>
        """,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    notify_failure = build_notify_task(
        task_id="notify_ml_failure",
        subject="[Airflow] ml_pipeline failed",
        html_content="""
        <p>DAG <b>ml_pipeline</b> da that bai.</p>
        <p>Thoi gian xu ly: {{ ds }}.</p>
        <p>Vui long kiem tra log tren Airflow.</p>
        """,
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    tracked_tasks = []
    for task_name in ML_TASKS:
        train_task = build_train_task(task_name)
        predict_task = build_predict_task(task_name)
        tracked_tasks.extend([train_task, predict_task])
        start >> train_task >> predict_task >> end

    tracked_tasks >> notify_failure
    end >> notify_success
