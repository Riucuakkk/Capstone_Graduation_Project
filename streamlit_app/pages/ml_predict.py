from __future__ import annotations

import sys
import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ml.service import make_prediction_output, prepare_inference_frame, summarize_for_genai
from src.ml.tasks import get_task, list_tasks
from streamlit_app.components.charts import bar_chart, donut_chart
from streamlit_app.components.db_connection import database_is_ready, read_sql


st.set_page_config(page_title="ML Predict", page_icon="🤖", layout="wide")


def load_css() -> None:
    css_path = Path(__file__).resolve().parents[1] / "assets" / "style.css"
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def model_path(task_name: str) -> Path:
    return ROOT / "src" / "ml" / "models" / f"{task_name}.joblib"


def metadata_path(task_name: str) -> Path:
    return ROOT / "src" / "ml" / "models" / f"{task_name}.json"


def load_model(task_name: str):
    return joblib.load(model_path(task_name))


def load_frame(task_name: str, limit: int) -> pd.DataFrame:
    task = get_task(task_name)
    sql = task.source_sql.strip()
    if task.where_clause:
        sql = f"{sql}\n{task.where_clause}"
    if limit > 0:
        sql = f"select * from ({sql}) app_source limit {int(limit)}"
    return read_sql(sql)


def resolve_scores(model, task, X: pd.DataFrame):
    if task.problem_type != "classification" or not hasattr(model, "predict_proba"):
        return None
    probabilities = model.predict_proba(X)
    classes = list(getattr(model, "classes_", []))
    if task.positive_class_label in classes:
        return probabilities[:, classes.index(task.positive_class_label)]
    return probabilities.max(axis=1)


load_css()
st.title("ML Predict")
st.caption("Chay inference tu artifact da train va bien prediction thanh action nghiep vu.")

ready, message = database_is_ready()
if not ready:
    st.error("Postgres chua san sang.")
    st.code(message, language="text")
    st.stop()

tasks = list_tasks()
task_names = [task.name for task in tasks]
selected_task = st.selectbox("ML Task", task_names, format_func=lambda name: f"{name} - {get_task(name).prediction_name}")
task = get_task(selected_task)

with st.expander("Mo ta bai toan", expanded=True):
    st.write(task.business_goal)
    st.write("Entity:", task.entity_name)
    st.write("Feature columns:", ", ".join(task.numeric_features + task.categorical_features))

artifact_exists = model_path(selected_task).exists()
if not artifact_exists:
    st.warning(
        "Chua co model artifact cho task nay. Hay train truoc bang CLI: "
        f"`python -m src.ml.train_model --task {selected_task}`"
    )
    st.stop()

limit = st.slider("Rows to score", min_value=10, max_value=1000, value=100, step=10)

try:
    df = load_frame(selected_task, limit)
    model = load_model(selected_task)
    ids, X = prepare_inference_frame(df, task)
    predictions = model.predict(X)
    scores = resolve_scores(model, task, X)
    output = make_prediction_output(task, ids, predictions, scores)
except Exception as exc:
    st.error("Khong chay duoc inference cho task nay.")
    st.code(str(exc), language="text")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Rows scored", f"{len(output):,}")
col2.metric("Problem", task.problem_type)
col3.metric("Model", model_path(selected_task).name)

if metadata_path(selected_task).exists():
    st.markdown('<div class="section-title">Training Metrics</div>', unsafe_allow_html=True)
    metadata = json.loads(metadata_path(selected_task).read_text(encoding="utf-8"))
    metric_values = metadata.get("metrics", {})
    if isinstance(metric_values, dict):
        metric_cols = st.columns(max(1, len(metric_values)))
        for col, (name, value) in zip(metric_cols, metric_values.items()):
            col.metric(name, f"{float(value):.4f}")

left, right = st.columns((1, 2))
with left:
    if "risk_band" in output.columns:
        band_counts = output["risk_band"].fillna("unknown").value_counts().reset_index()
        band_counts.columns = ["risk_band", "rows"]
        st.plotly_chart(donut_chart(band_counts, "risk_band", "rows", "Risk distribution"), use_container_width=True)
with right:
    if "prediction" in output.columns:
        pred_counts = output["prediction"].astype(str).value_counts().head(12).reset_index()
        pred_counts.columns = ["prediction", "rows"]
        st.plotly_chart(bar_chart(pred_counts, "prediction", "rows", "Prediction distribution"), use_container_width=True)

st.markdown('<div class="section-title">Prediction Preview</div>', unsafe_allow_html=True)
st.dataframe(output, use_container_width=True, hide_index=True)

with st.expander("GenAI-ready summary"):
    st.json(summarize_for_genai(task, output))
