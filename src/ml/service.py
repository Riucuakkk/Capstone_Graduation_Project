from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any
from uuid import uuid4

import joblib
import pandas as pd
from psycopg2.extras import Json, execute_values
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.ml.tasks import TaskConfig, get_task, list_tasks
from src.utils.db_connection import get_connection


# Cau hinh chung cho toan bo nghiep vu ML: noi luu model, ti le test va seed.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / "src" / "ml" / "models"
DEFAULT_TEST_SIZE = 0.2
DEFAULT_RANDOM_STATE = 42


def _normalize_scalar(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _normalize_score(value: Any) -> float | None:
    normalized = _normalize_scalar(value)
    return None if normalized is None else float(normalized)


# Nhom ham doc du lieu tu mart. Moi task tu dinh nghia SQL trong tasks.py.
def read_sql_frame(sql: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql(sql, conn)
    finally:
        conn.close()


def load_task_frame(task: TaskConfig) -> pd.DataFrame:
    sql = task.source_sql.strip()
    if task.where_clause:
        sql = f"{sql}\n{task.where_clause}"
    return read_sql_frame(sql)


# Nhom ham luu va doc artifact sau khi train de predict co the tai lai model.
def ensure_model_dir() -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_DIR


def artifact_base_path(task_name: str) -> Path:
    return ensure_model_dir() / task_name


def save_training_artifacts(task_name: str, pipeline, metadata: dict) -> dict[str, str]:
    base_path = artifact_base_path(task_name)
    model_path = base_path.with_suffix(".joblib")
    metadata_path = base_path.with_suffix(".json")

    joblib.dump(pipeline, model_path)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return {
        "model_path": str(model_path),
        "metadata_path": str(metadata_path),
    }


def load_model(task_name: str):
    return joblib.load(artifact_base_path(task_name).with_suffix(".joblib"))


def load_metadata(task_name: str) -> dict:
    metadata_path = artifact_base_path(task_name).with_suffix(".json")
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def ensure_tracking_tables() -> None:
    ddl = """
    create schema if not exists ml;

    create table if not exists ml.training_runs (
        id bigserial primary key,
        external_run_id text not null unique,
        task_name text not null,
        problem_type text not null,
        prediction_name text not null,
        business_goal text not null,
        train_rows integer not null,
        test_rows integer not null,
        split_strategy text not null,
        metrics_json jsonb not null,
        model_path text not null,
        metadata_path text not null,
        created_at timestamptz not null default now()
    );

    create table if not exists ml.predictions (
        id bigserial primary key,
        prediction_run_id text not null,
        source_run_id text,
        task_name text not null,
        entity_name text not null,
        prediction_name text not null,
        ids_json jsonb not null,
        prediction_value text,
        prediction_score double precision,
        risk_band text,
        recommended_action text,
        business_goal text not null,
        model_metrics_json jsonb not null,
        created_at timestamptz not null default now()
    );

    create index if not exists idx_ml_predictions_run_id on ml.predictions (prediction_run_id);
    create index if not exists idx_ml_predictions_task_name on ml.predictions (task_name);
    """

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(ddl)
    finally:
        conn.close()


def persist_training_run(
    task: TaskConfig,
    training_result: dict[str, Any],
    artifact_paths: dict[str, str],
    run_id: str | None = None,
) -> dict[str, Any]:
    ensure_tracking_tables()
    external_run_id = run_id or f"{task.name}-train-{uuid4().hex[:12]}"

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "delete from ml.training_runs where external_run_id = %s",
                    (external_run_id,),
                )
                cursor.execute(
                    """
                    insert into ml.training_runs (
                        external_run_id,
                        task_name,
                        problem_type,
                        prediction_name,
                        business_goal,
                        train_rows,
                        test_rows,
                        split_strategy,
                        metrics_json,
                        model_path,
                        metadata_path
                    )
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    returning external_run_id, created_at
                    """,
                    (
                        external_run_id,
                        task.name,
                        task.problem_type,
                        task.prediction_name,
                        task.business_goal,
                        int(training_result["train_rows"]),
                        int(training_result["test_rows"]),
                        training_result["split_strategy"],
                        Json(training_result["metrics"]),
                        artifact_paths["model_path"],
                        artifact_paths["metadata_path"],
                    ),
                )
                saved_run_id, created_at = cursor.fetchone()
    finally:
        conn.close()

    return {
        "external_run_id": saved_run_id,
        "created_at": created_at.isoformat(),
    }


def persist_prediction_output(
    task: TaskConfig,
    output: pd.DataFrame,
    model_metrics: dict[str, Any],
    run_id: str | None = None,
    source_run_id: str | None = None,
) -> dict[str, Any]:
    ensure_tracking_tables()
    prediction_run_id = run_id or f"{task.name}-predict-{uuid4().hex[:12]}"
    rows: list[tuple[Any, ...]] = []

    for record in output.to_dict(orient="records"):
        ids_json = {column: _normalize_scalar(record.get(column)) for column in task.id_columns}
        prediction_value = _normalize_scalar(record.get("prediction"))
        rows.append(
            (
                prediction_run_id,
                source_run_id,
                task.name,
                task.entity_name,
                task.prediction_name,
                Json(ids_json),
                None if prediction_value is None else str(prediction_value),
                _normalize_score(record.get("prediction_score")),
                _normalize_scalar(record.get("risk_band")),
                _normalize_scalar(record.get("recommended_action")),
                task.business_goal,
                Json(model_metrics),
            )
        )

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "delete from ml.predictions where prediction_run_id = %s",
                    (prediction_run_id,),
                )
                if rows:
                    execute_values(
                        cursor,
                        """
                        insert into ml.predictions (
                            prediction_run_id,
                            source_run_id,
                            task_name,
                            entity_name,
                            prediction_name,
                            ids_json,
                            prediction_value,
                            prediction_score,
                            risk_band,
                            recommended_action,
                            business_goal,
                            model_metrics_json
                        )
                        values %s
                        """,
                        rows,
                    )
    finally:
        conn.close()

    return {
        "prediction_run_id": prediction_run_id,
        "rows_written": len(rows),
        "source_run_id": source_run_id,
    }


# Nhom ham bien doi du lieu thanh X/y/id va dung pipeline sklearn.
def split_features_and_target(df: pd.DataFrame, task: TaskConfig):
    feature_columns = task.numeric_features + task.categorical_features
    selected_columns = task.id_columns + feature_columns + [task.target_column]
    if task.time_column:
        selected_columns.append(task.time_column)

    clean_df = df[selected_columns].copy()
    clean_df = clean_df.dropna(subset=[task.target_column]).reset_index(drop=True)

    X = clean_df[feature_columns]
    y = clean_df[task.target_column]
    ids = clean_df[task.id_columns]
    split_values = clean_df[task.time_column] if task.time_column else None
    return X, y, ids, split_values


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


def _time_based_split(X, y, ids, split_values, test_size: float):
    ordered = (
        pd.DataFrame({"_split_value": pd.to_datetime(split_values, errors="coerce")})
        .reset_index()
        .sort_values(by=["_split_value", "index"], kind="stable")
    )
    split_at = max(1, int(len(ordered) * (1 - test_size)))
    split_at = min(split_at, len(ordered) - 1)

    train_idx = ordered.iloc[:split_at]["index"]
    test_idx = ordered.iloc[split_at:]["index"]

    return (
        X.iloc[train_idx],
        X.iloc[test_idx],
        y.iloc[train_idx],
        y.iloc[test_idx],
        ids.iloc[train_idx],
        ids.iloc[test_idx],
        "time",
    )


def train_task(df: pd.DataFrame, task: TaskConfig) -> dict:
    X, y, ids, split_values = split_features_and_target(df, task)
    if len(X) < 2:
        raise ValueError(f"Task '{task.name}' does not have enough rows to train.")

    if task.time_column and split_values is not None and split_values.notna().sum() >= 2:
        X_train, X_test, y_train, y_test, ids_train, ids_test, split_strategy = _time_based_split(
            X,
            y,
            ids,
            split_values,
            DEFAULT_TEST_SIZE,
        )
    else:
        X_train, X_test, y_train, y_test, ids_train, ids_test = train_test_split(
            X,
            y,
            ids,
            test_size=DEFAULT_TEST_SIZE,
            random_state=DEFAULT_RANDOM_STATE,
            stratify=y if task.problem_type == "classification" else None,
        )
        split_strategy = "random"

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
        "split_strategy": split_strategy,
        "feature_columns": list(X.columns),
        "sample_prediction_keys": ids_test.head(10).to_dict(orient="records"),
        "task": asdict(task),
    }


def prepare_inference_frame(df: pd.DataFrame, task: TaskConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    feature_columns = task.numeric_features + task.categorical_features
    ids = df[task.id_columns].copy()
    X = df[feature_columns].copy()
    return ids, X


# Nhom ham gan y nghia nghiep vu cho output: risk band, action va GenAI summary.
def _score_to_risk_band(score: float | None) -> str | None:
    if score is None:
        return None
    if score >= 0.8:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"


def _regression_to_band(task: TaskConfig, value: float | int | None) -> str | None:
    if value is None:
        return None
    numeric_value = float(value)
    if numeric_value >= 0.8:
        return "high"
    if numeric_value >= 0.55:
        return "medium"
    return "low"


def recommend_action(task: TaskConfig, risk_band: str | None) -> str:
    if task.name == "product_bestseller":
        actions = {
            "high": "Prioritize inventory, promotion budget, and seller readiness for this product.",
            "medium": "Monitor demand trend and prepare limited campaign support.",
            "low": "Keep standard assortment monitoring.",
        }
    elif task.name == "order_success":
        actions = {
            "high": "Keep normal fulfillment flow and prioritize high-value successful orders.",
            "medium": "Review payment and fulfillment signals to protect conversion.",
            "low": "Flag for operations review because this order may not complete successfully.",
        }
    elif task.name == "geo_high_demand":
        actions = {
            "high": "Increase campaign focus and logistics readiness for this location.",
            "medium": "Monitor regional demand and prepare targeted offers.",
            "low": "Keep standard regional planning.",
        }
    else:
        actions = {
            "high": "Flag for business review.",
            "medium": "Monitor with a standard review workflow.",
            "low": "No immediate action required.",
        }
    return actions.get(risk_band or "low", "No immediate action required.")


def make_prediction_output(task: TaskConfig, ids: pd.DataFrame, predictions, scores=None) -> pd.DataFrame:
    output = ids.copy()
    output["prediction"] = predictions

    if task.problem_type == "classification":
        score_series = pd.Series(scores if scores is not None else [None] * len(output))
        output["prediction_score"] = score_series
        output["risk_band"] = output["prediction_score"].apply(_score_to_risk_band)
    else:
        output["prediction_score"] = None
        output["risk_band"] = output["prediction"].apply(lambda value: _regression_to_band(task, value))

    output["prediction_name"] = task.prediction_name
    output["entity_name"] = task.entity_name
    output["business_goal"] = task.business_goal
    output["recommended_action"] = output["risk_band"].apply(lambda band: recommend_action(task, band))
    return output


def summarize_for_genai(task: TaskConfig, output: pd.DataFrame) -> dict[str, Any]:
    preview = output.head(20).to_dict(orient="records")
    band_counts = (
        output["risk_band"].fillna("unknown").value_counts().to_dict()
        if "risk_band" in output.columns
        else {}
    )

    return {
        "task_name": task.name,
        "prediction_name": task.prediction_name,
        "entity_name": task.entity_name,
        "business_goal": task.business_goal,
        "example_questions": list(task.example_questions),
        "risk_band_distribution": band_counts,
        "preview": preview,
    }


def _resolve_classification_scores(model, task, X):
    if not hasattr(model, "predict_proba"):
        return None

    probabilities = model.predict_proba(X)
    classes = list(getattr(model, "classes_", []))

    if task.positive_class_label in classes:
        class_index = classes.index(task.positive_class_label)
        return probabilities[:, class_index]

    return probabilities.max(axis=1)


# API chinh cho CLI/API layer: train model, predict va liet ke catalog task.
def train_service(task_name: str, persist_run: bool = False, run_id: str | None = None) -> dict:
    task = get_task(task_name)
    df = load_task_frame(task)
    training_result = train_task(df, task)

    artifact_paths = save_training_artifacts(
        task_name,
        training_result["pipeline"],
        {
            "task": training_result["task"],
            "metrics": training_result["metrics"],
            "train_rows": training_result["train_rows"],
            "test_rows": training_result["test_rows"],
            "split_strategy": training_result["split_strategy"],
            "feature_columns": training_result["feature_columns"],
            "sample_prediction_keys": training_result["sample_prediction_keys"],
        },
    )

    result = {
        "task_name": task_name,
        "problem_type": task.problem_type,
        "prediction_name": task.prediction_name,
        "business_goal": task.business_goal,
        "metrics": training_result["metrics"],
        "train_rows": training_result["train_rows"],
        "test_rows": training_result["test_rows"],
        "split_strategy": training_result["split_strategy"],
        **artifact_paths,
    }

    if persist_run:
        result["training_run"] = persist_training_run(task, training_result, artifact_paths, run_id)

    return result


def predict_service(
    task_name: str,
    limit: int,
    write_output: bool = False,
    run_id: str | None = None,
    source_run_id: str | None = None,
) -> dict:
    task = get_task(task_name)
    model = load_model(task_name)
    metadata = load_metadata(task_name)

    df = load_task_frame(task)
    if limit > 0:
        df = df.head(limit).copy()

    ids, X = prepare_inference_frame(df, task)
    predictions = model.predict(X)

    score_values = None
    if task.problem_type == "classification":
        score_values = _resolve_classification_scores(model, task, X)

    output = make_prediction_output(task, ids, predictions, score_values)

    result = {
        "task_name": task_name,
        "model_metrics": metadata.get("metrics", {}),
        "rows_scored": int(len(output)),
        "prediction_preview": output.head(20).to_dict(orient="records"),
        "genai_summary": summarize_for_genai(task, output),
    }

    if write_output:
        result["prediction_run"] = persist_prediction_output(
            task,
            output,
            metadata.get("metrics", {}),
            run_id=run_id,
            source_run_id=source_run_id,
        )

    return result


def task_catalog() -> list[dict]:
    return [
        {
            "task_name": task.name,
            "problem_type": task.problem_type,
            "entity_name": task.entity_name,
            "prediction_name": task.prediction_name,
            "business_goal": task.business_goal,
            "example_questions": list(task.example_questions),
        }
        for task in list_tasks()
    ]
