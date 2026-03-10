from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "hopnh",
    "start_date": datetime(2024, 1, 1),
}

with DAG(
    dag_id="staging_pipeline",
    default_args=default_args,
    schedule_interval=None,
    catchup=False
) as dag:

    dbt_staging = BashOperator(
        task_id="run_dbt_staging",
        bash_command="""
        cd /opt/airflow/dbt &&
        dbt run --select staging
        """
    )

    dbt_staging