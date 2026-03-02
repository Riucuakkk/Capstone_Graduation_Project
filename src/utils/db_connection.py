
import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="ecommerce",
        user="airflow",
        password="airflow"
    )
