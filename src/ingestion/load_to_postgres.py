
import pandas as pd
from sqlalchemy import create_engine
import os

def load_all_csv():
    engine = create_engine(
        "postgresql://airflow:airflow@localhost:5432/ecommerce"
    )

    raw_path = os.path.join("data", "raw")

    for file in os.listdir(raw_path):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(raw_path, file))
            table_name = file.replace(".csv", "")
            df.to_sql(table_name, engine, if_exists="replace", index=False)
