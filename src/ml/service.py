from __future__ import annotations

from src.ml.artifacts import load_metadata, load_model, save_training_artifacts
from src.ml.data_access import read_sql_frame
from src.ml.pipeline import load_task_frame, prepare_inference_frame, train_task
from src.ml.semantic import make_prediction_output, summarize_for_genai
from src.ml.tasks import get_task, list_tasks


def train_service(task_name: str) -> dict:
    task = get_task(task_name)
    df = load_task_frame(task, read_sql_frame)
    training_result = train_task(df, task)

    artifact_paths = save_training_artifacts(
        task_name,
        training_result["pipeline"],
        {
            "task": training_result["task"],
            "metrics": training_result["metrics"],
            "train_rows": training_result["train_rows"],
            "test_rows": training_result["test_rows"],
            "feature_columns": training_result["feature_columns"],
            "sample_prediction_keys": training_result["sample_prediction_keys"],
        },
    )

    return {
        "task_name": task_name,
        "problem_type": task.problem_type,
        "prediction_name": task.prediction_name,
        "business_goal": task.business_goal,
        "metrics": training_result["metrics"],
        "train_rows": training_result["train_rows"],
        "test_rows": training_result["test_rows"],
        **artifact_paths,
    }


def predict_service(task_name: str, limit: int) -> dict:
    task = get_task(task_name)
    model = load_model(task_name)
    metadata = load_metadata(task_name)

    df = load_task_frame(task, read_sql_frame)
    if limit > 0:
        df = df.head(limit).copy()

    ids, X = prepare_inference_frame(df, task)
    predictions = model.predict(X)

    score_values = None
    if task.problem_type == "classification" and hasattr(model, "predict_proba"):
        score_values = model.predict_proba(X).max(axis=1)

    output = make_prediction_output(task, ids, predictions, score_values)

    return {
        "task_name": task_name,
        "model_metrics": metadata.get("metrics", {}),
        "rows_scored": int(len(output)),
        "prediction_preview": output.head(20).to_dict(orient="records"),
        "genai_summary": summarize_for_genai(task, output),
    }


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
