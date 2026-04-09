from __future__ import annotations

from dataclasses import asdict

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.ml.config import DEFAULT_RANDOM_STATE, DEFAULT_TEST_SIZE
from src.ml.tasks import TaskConfig


def load_task_frame(task: TaskConfig, reader) -> pd.DataFrame:
    sql = task.source_sql.strip()
    if task.where_clause:
        sql = f"{sql}\n{task.where_clause}"
    return reader(sql)


def split_features_and_target(df: pd.DataFrame, task: TaskConfig):
    feature_columns = task.numeric_features + task.categorical_features
    clean_df = df[task.id_columns + feature_columns + [task.target_column]].copy()
    clean_df = clean_df.dropna(subset=[task.target_column])

    X = clean_df[feature_columns]
    y = clean_df[task.target_column]
    ids = clean_df[task.id_columns]
    return X, y, ids


def build_model_pipeline(task: TaskConfig) -> Pipeline:
    numeric_pipeline = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median"))]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, task.numeric_features),
            ("cat", categorical_pipeline, task.categorical_features),
        ],
        remainder="drop",
    )

    if task.problem_type == "classification":
        estimator = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=DEFAULT_RANDOM_STATE,
            n_jobs=-1,
        )
    else:
        estimator = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            random_state=DEFAULT_RANDOM_STATE,
            n_jobs=-1,
        )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", estimator),
        ]
    )


def train_task(df: pd.DataFrame, task: TaskConfig) -> dict:
    X, y, ids = split_features_and_target(df, task)
    X_train, X_test, y_train, y_test, ids_train, ids_test = train_test_split(
        X,
        y,
        ids,
        test_size=DEFAULT_TEST_SIZE,
        random_state=DEFAULT_RANDOM_STATE,
        stratify=y if task.problem_type == "classification" else None,
    )

    pipeline = build_model_pipeline(task)
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    if task.problem_type == "classification":
        metrics = {
            "accuracy": float(accuracy_score(y_test, predictions)),
            "f1_weighted": float(f1_score(y_test, predictions, average="weighted")),
        }
    else:
        metrics = {
            "rmse": float(mean_squared_error(y_test, predictions, squared=False)),
            "mae": float(mean_absolute_error(y_test, predictions)),
            "r2": float(r2_score(y_test, predictions)),
        }

    return {
        "pipeline": pipeline,
        "metrics": metrics,
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "feature_columns": list(X.columns),
        "sample_prediction_keys": ids_test.head(10).to_dict(orient="records"),
        "task": asdict(task),
    }


def prepare_inference_frame(df: pd.DataFrame, task: TaskConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    feature_columns = task.numeric_features + task.categorical_features
    ids = df[task.id_columns].copy()
    X = df[feature_columns].copy()
    return ids, X
