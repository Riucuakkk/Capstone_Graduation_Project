import json
from pathlib import Path

import joblib

from src.ml.config import ensure_model_dir


def artifact_base_path(task_name: str) -> Path:
    model_dir = ensure_model_dir()
    return model_dir / task_name


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
    model_path = artifact_base_path(task_name).with_suffix(".joblib")
    return joblib.load(model_path)


def load_metadata(task_name: str) -> dict:
    metadata_path = artifact_base_path(task_name).with_suffix(".json")
    return json.loads(metadata_path.read_text(encoding="utf-8"))
