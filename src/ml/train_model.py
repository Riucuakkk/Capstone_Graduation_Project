
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
from src.utils.db_connection import get_connection

def train():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM olist_order_items_dataset", conn)

    X = df[["price", "freight_value"]]
    y = df["price"]

    X_train, X_test, y_train, y_test = train_test_split(X, y)

    model = RandomForestRegressor()
    model.fit(X_train, y_train)

    joblib.dump(model, "model.pkl")

if __name__ == "__main__":
    train()
