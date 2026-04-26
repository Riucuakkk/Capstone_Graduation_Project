from __future__ import annotations

import sys
import json
from pathlib import Path

import joblib
import numpy as np
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


# Chỉ các trường cốt lõi cần nhập tay cho từng task.
# Numeric: (col, label, default, min, max)  — default=int → ô nguyên, float → ô thập phân
# Categorical: (col, label, [options])
CORE_FIELDS: dict[str, dict] = {
    "product_bestseller": {
        "numeric": [
            ("trailing_7_sale_day_avg_items", "TB bán/ngày 7 ngày qua", 5.0, 0.0, 500.0),
            ("total_items",                  "Tổng đã bán (lịch sử)",    50.0, 0.0, 10000.0),
            ("calendar_month",               "Tháng",                    6,    1,   12),
            ("delivered_late_ratio",         "Tỉ lệ giao trễ (0–1)",     0.1,  0.0, 1.0),
        ],
        "categorical": [
            ("product_category", "Danh mục sản phẩm", [
                "cama_mesa_banho", "beleza_saude", "esporte_lazer",
                "informatica_acessorios", "moveis_decoracao", "utilidades_domesticas",
                "relogios_presentes", "ferramentas_jardim", "automotivo", "brinquedos",
            ]),
        ],
    },
    "order_success": {
        "numeric": [
            ("total_gross_amount",        "Giá trị đơn hàng (R$)",     150.0, 0.0, 5000.0),
            ("approval_lead_hours",       "Giờ chờ duyệt đơn",          1.0,  0.0, 72.0),
            ("max_payment_installments",  "Số kỳ trả góp tối đa",        1,    1,   24),
        ],
        "categorical": [
            ("dominant_payment_type", "Loại thanh toán chính", [
                "credit_card", "boleto", "voucher", "debit_card",
            ]),
            ("customer_state", "Bang/Tỉnh khách hàng", [
                "SP", "RJ", "MG", "RS", "PR", "SC", "BA", "DF", "GO", "PE",
            ]),
        ],
    },
    "geo_high_demand": {
        "numeric": [
            ("trailing_7_sale_day_avg_orders", "Đơn TB/ngày 7 ngày qua",       2.0, 0.0, 200.0),
            ("avg_review_score",               "Điểm đánh giá TB (1–5)",        4.0, 1.0, 5.0),
            ("calendar_month",                 "Tháng",                          6,   1,   12),
        ],
        "categorical": [
            ("customer_state", "Bang/Tỉnh", [
                "SP", "RJ", "MG", "RS", "PR", "SC", "BA", "DF", "GO", "PE",
            ]),
        ],
    },
}


def _build_single_row(task, user_inputs: dict) -> pd.DataFrame:
    """Tạo 1 dòng DataFrame đủ cột feature; cột không nhập để NaN → imputer xử lý."""
    row: dict = {col: np.nan for col in task.numeric_features + task.categorical_features}
    row.update(user_inputs)
    for id_col in task.id_columns:
        row[id_col] = "manual"
    return pd.DataFrame([row])


def _risk_color(risk: str) -> str:
    return {"high": "#e74c3c", "medium": "#f39c12", "low": "#27ae60"}.get(risk, "#888888")


def render_single_predict(task, model) -> None:
    st.caption("Chỉ nhập các thông số cốt lõi — biến còn lại dùng giá trị median từ training data.")

    core = CORE_FIELDS.get(task.name, {"numeric": [], "categorical": []})
    user_inputs: dict = {}

    with st.form("single_predict_form"):
        cols = st.columns(2)
        for i, (col_name, label, default, min_val, max_val) in enumerate(core["numeric"]):
            with cols[i % 2]:
                if isinstance(default, int):
                    user_inputs[col_name] = st.number_input(
                        label, min_value=int(min_val), max_value=int(max_val),
                        value=int(default), step=1,
                    )
                else:
                    user_inputs[col_name] = st.number_input(
                        label, min_value=float(min_val), max_value=float(max_val),
                        value=float(default), step=0.1, format="%.2f",
                    )

        for col_name, label, options in core["categorical"]:
            user_inputs[col_name] = st.selectbox(label, options)

        submitted = st.form_submit_button("Dự đoán", use_container_width=True, type="primary")

    if not submitted:
        return

    try:
        df = _build_single_row(task, user_inputs)
        ids, X = prepare_inference_frame(df, task)
        prediction = model.predict(X)
        scores = resolve_scores(model, task, X)
        output = make_prediction_output(task, ids, prediction, scores)
    except Exception as exc:
        st.error(f"Lỗi khi dự đoán: {exc}")
        return

    row = output.iloc[0]
    risk = str(row.get("risk_band", "unknown"))
    score = row.get("prediction_score")
    action = str(row.get("recommended_action", ""))
    pred_val = row.get("prediction")
    color = _risk_color(risk)
    score_str = f"{float(score):.2%}" if score is not None and not pd.isna(score) else "N/A"

    st.markdown(
        f"""
        <div style="padding:1.2rem;border-radius:8px;background:{color}18;
                    border-left:5px solid {color};margin-top:1rem">
            <div style="font-size:1.1rem;font-weight:600;margin-bottom:.4rem">
                Kết quả: <span style="color:{color}">{pred_val}</span>
                &nbsp;·&nbsp; Risk band: <span style="color:{color}">{risk.upper()}</span>
                &nbsp;·&nbsp; Score: {score_str}
            </div>
            <div style="color:#555">💡 {action}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─── Main ─────────────────────────────────────────────────────────────────────

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
selected_task = st.selectbox(
    "ML Task", task_names,
    format_func=lambda name: f"{name} — {get_task(name).prediction_name}",
)
task = get_task(selected_task)

if not model_path(selected_task).exists():
    st.warning(
        "Chua co model artifact cho task nay. Hay train truoc bang CLI: "
        f"`python -m src.ml.train_model --task {selected_task}`"
    )
    st.stop()

model = load_model(selected_task)

tab_single, tab_batch = st.tabs(["Single Predict (nhập tay)", "Batch Score (từ DB)"])

# ── Tab: Single Predict ──────────────────────────────────────────────────────
with tab_single:
    render_single_predict(task, model)

# ── Tab: Batch Score ─────────────────────────────────────────────────────────
with tab_batch:
    with st.expander("Mô tả bài toán", expanded=False):
        st.write(task.business_goal)
        st.write("Entity:", task.entity_name)
        st.write("Feature columns:", ", ".join(task.numeric_features + task.categorical_features))

    limit = st.slider("Rows to score", min_value=10, max_value=1000, value=100, step=10)

    batch_ok = True
    try:
        df_batch = load_frame(selected_task, limit)
        ids_batch, X_batch = prepare_inference_frame(df_batch, task)
        predictions_batch = model.predict(X_batch)
        scores_batch = resolve_scores(model, task, X_batch)
        output_batch = make_prediction_output(task, ids_batch, predictions_batch, scores_batch)
    except Exception as exc:
        st.error("Khong chay duoc inference cho task nay.")
        st.code(str(exc), language="text")
        batch_ok = False

    if batch_ok:
        col1, col2, col3 = st.columns(3)
        col1.metric("Rows scored", f"{len(output_batch):,}")
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
            if "risk_band" in output_batch.columns:
                band_counts = output_batch["risk_band"].fillna("unknown").value_counts().reset_index()
                band_counts.columns = ["risk_band", "rows"]
                st.plotly_chart(
                    donut_chart(band_counts, "risk_band", "rows", "Risk distribution"),
                    use_container_width=True,
                )
        with right:
            if "prediction" in output_batch.columns:
                pred_counts = output_batch["prediction"].astype(str).value_counts().head(12).reset_index()
                pred_counts.columns = ["prediction", "rows"]
                st.plotly_chart(
                    bar_chart(pred_counts, "prediction", "rows", "Prediction distribution"),
                    use_container_width=True,
                )

        st.markdown('<div class="section-title">Prediction Preview</div>', unsafe_allow_html=True)
        st.dataframe(output_batch, use_container_width=True, hide_index=True)

        with st.expander("GenAI-ready summary"):
            st.json(summarize_for_genai(task, output_batch))
