from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / "src" / "ml" / "models"
DEFAULT_TEST_SIZE = 0.2
DEFAULT_RANDOM_STATE = 42


def ensure_model_dir() -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_DIR
