from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append("/opt/airflow")

# Import project modules
from src.ingestion.load_to_postgres import load_all_csv
from src.data_quality.raw_checks import run_all_raw_checks
from src.data_quality.staging_checks import run_all_staging_checks
from src.data_quality.mart_checks import run_all_mart_checks
from src.ml.train_model import train


# ========================
# Default Arguments
# ========================
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1
}


# ========================
# DAG Definition
# ========================
with DAG(
    dag_id="ecommerce_production_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    description="Full Production Ecommerce Data Pipeline"
) as dag:

    start = EmptyOperator(task_id="start_pipeline")

    # ------------------------
    # Create Schemas
    # ------------------------
    create_schemas = BashOperator(
        task_id="create_schemas",
        bash_command="""
        psql postgresql://airflow:airflow@postgres:5432/ecommerce -c "
        CREATE SCHEMA IF NOT EXISTS raw;
        CREATE SCHEMA IF NOT EXISTS staging;
        CREATE SCHEMA IF NOT EXISTS mart;
        "
        """
    )

    # ------------------------
    # Ingestion
    # ------------------------
    ingestion = PythonOperator(
        task_id="load_raw_data",
        python_callable=load_all_csv
    )

    # ------------------------
    # Raw Data Quality
    # ------------------------
    raw_dq = PythonOperator(
        task_id="raw_data_quality_checks",
        python_callable=run_all_raw_checks
    )

    # ------------------------
    # Run dbt
    # ------------------------
    run_dbt = BashOperator(
        task_id="run_dbt_models",
        bash_command="""
        cd /opt/airflow/dbt && dbt run
        """
    )

    # ------------------------
    # Staging DQ
    # ------------------------
    staging_dq = PythonOperator(
        task_id="staging_data_quality_checks",
        python_callable=run_all_staging_checks
    )

    # ------------------------
    # Mart DQ
    # ------------------------
    mart_dq = PythonOperator(
        task_id="mart_data_quality_checks",
        python_callable=run_all_mart_checks
    )

    # ------------------------
    # Train ML Model
    # ------------------------
    train_model = PythonOperator(
        task_id="train_ml_model",
        python_callable=train
    )

    end = EmptyOperator(task_id="end_pipeline")

    # ========================
    # Task Dependencies
    # ========================
    start >> create_schemas >> ingestion >> raw_dq
    raw_dq >> run_dbt >> staging_dq >> mart_dq
    mart_dq >> train_model >> end