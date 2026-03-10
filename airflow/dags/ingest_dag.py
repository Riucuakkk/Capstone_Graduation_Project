from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="ingest_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    description="Init DB and ingest source data"
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

    init_db >> ingest_data