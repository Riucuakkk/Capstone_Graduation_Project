from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.db_connection import database_is_ready, db_config
from src.ml.tasks import get_task


st.set_page_config(
    page_title="E-commerce ML & BI",
    page_icon="\U0001F4CA",
    layout="wide",
    initial_sidebar_state="expanded",
)

BUSINESS_TASKS = [
    {
        "task_name": "product_bestseller",
        "label": "D\u1ef1 \u0111o\u00e1n s\u1ea3n ph\u1ea9m b\u00e1n ch\u1ea1y",
        "caption": "\u01afu ti\u00ean t\u1ed3n kho v\u00e0 marketing cho s\u1ea3n ph\u1ea9m c\u00f3 kh\u1ea3 n\u0103ng b\u00e1n ch\u1ea1y trong 7 ng\u00e0y t\u1edbi.",
        "goal": "D\u1ef1 \u0111o\u00e1n li\u1ec7u m\u1ed9t s\u1ea3n ph\u1ea9m c\u00f3 thu\u1ed9c nh\u00f3m nhu c\u1ea7u cao trong 7 ng\u00e0y t\u1edbi hay kh\u00f4ng.",
        "questions": [
            "S\u1ea3n ph\u1ea9m n\u00e0o c\u00f3 kh\u1ea3 n\u0103ng b\u00e1n ch\u1ea1y trong 7 ng\u00e0y t\u1edbi?",
            "N\u00ean \u01b0u ti\u00ean t\u1ed3n kho ho\u1eb7c marketing cho s\u1ea3n ph\u1ea9m n\u00e0o?",
        ],
    },
    {
        "task_name": "order_success",
        "label": "D\u1ef1 \u0111o\u00e1n \u0111\u01a1n h\u00e0ng th\u00e0nh c\u00f4ng",
        "caption": "Ph\u00e1t hi\u1ec7n \u0111\u01a1n h\u00e0ng c\u1ea7n can thi\u1ec7p s\u1edbm \u0111\u1ec3 t\u0103ng t\u1ef7 l\u1ec7 giao th\u00e0nh c\u00f4ng.",
        "goal": "D\u1ef1 \u0111o\u00e1n li\u1ec7u m\u1ed9t \u0111\u01a1n h\u00e0ng c\u00f3 kh\u1ea3 n\u0103ng ho\u00e0n t\u1ea5t v\u00e0 giao th\u00e0nh c\u00f4ng hay kh\u00f4ng.",
        "questions": [
            "\u0110\u01a1n h\u00e0ng n\u00e0o c\u00f3 kh\u1ea3 n\u0103ng ho\u00e0n t\u1ea5t th\u00e0nh c\u00f4ng?",
            "\u0110\u01a1n n\u00e0o c\u1ea7n can thi\u1ec7p s\u1edbm \u0111\u1ec3 t\u0103ng t\u1ef7 l\u1ec7 giao th\u00e0nh c\u00f4ng?",
        ],
    },
    {
        "task_name": "geo_high_demand",
        "label": "D\u1ef1 b\u00e1o khu v\u1ef1c nhu c\u1ea7u cao",
        "caption": "X\u00e1c \u0111\u1ecbnh th\u00e0nh ph\u1ed1/khu v\u1ef1c c\u00f3 kh\u1ea3 n\u0103ng ph\u00e1t sinh nhu c\u1ea7u cao trong 7 ng\u00e0y t\u1edbi.",
        "goal": "D\u1ef1 \u0111o\u00e1n li\u1ec7u m\u1ed9t khu v\u1ef1c c\u00f3 tr\u1edf th\u00e0nh v\u00f9ng nhu c\u1ea7u cao trong 7 ng\u00e0y t\u1edbi hay kh\u00f4ng.",
        "questions": [
            "Khu v\u1ef1c n\u00e0o c\u00f3 kh\u1ea3 n\u0103ng mua h\u00e0ng cao trong 7 ng\u00e0y t\u1edbi?",
            "N\u00ean \u0111\u1ea9y campaign ho\u1eb7c chu\u1ea9n b\u1ecb logistics \u1edf \u0111\u1ecba \u0111i\u1ec3m n\u00e0o?",
        ],
    },
]

TASK_LABELS = {item["task_name"]: item["label"] for item in BUSINESS_TASKS}
TASK_CAPTIONS = {item["task_name"]: item["caption"] for item in BUSINESS_TASKS}
TASK_GOALS = {item["task_name"]: item["goal"] for item in BUSINESS_TASKS}
TASK_QUESTIONS = {item["task_name"]: item["questions"] for item in BUSINESS_TASKS}
DEFAULT_SUPERSET_DASHBOARD_URL = "http://localhost:8088/dashboard/list/"
SUPERSET_DASHBOARDS = [
    {
        "label": "Dashboard Sản phẩm bán chạy",
        "caption": "Mở dashboard Superset cho use case product bestseller.",
        "env_var": "SUPERSET_PRODUCT_BESTSELLER_DASHBOARD_URL",
    },
    {
        "label": "Dashboard Đơn hàng thành công",
        "caption": "Mở dashboard Superset cho use case order success.",
        "env_var": "SUPERSET_ORDER_SUCCESS_DASHBOARD_URL",
    },
    {
        "label": "Dashboard Khu vực nhu cầu cao",
        "caption": "Mở dashboard Superset cho use case geo demand.",
        "env_var": "SUPERSET_GEO_DEMAND_DASHBOARD_URL",
    },
]


def load_css() -> None:
    css_path = Path(__file__).parent / "assets" / "style.css"
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def init_state() -> None:
    st.session_state.setdefault("view", "home")
    st.session_state.setdefault("selected_task", None)


def go_to(view: str, task_name: str | None = None) -> None:
    st.session_state["view"] = view
    st.session_state["selected_task"] = task_name


def redirect(view: str, task_name: str | None = None) -> None:
    go_to(view, task_name)
    st.rerun()


def model_path(task_name: str) -> Path:
    return ROOT / "src" / "ml" / "models" / f"{task_name}.joblib"


def metadata_path(task_name: str) -> Path:
    return ROOT / "src" / "ml" / "models" / f"{task_name}.json"


def superset_dashboard_fallback_url() -> str:
    return os.getenv("SUPERSET_DASHBOARD_URL", DEFAULT_SUPERSET_DASHBOARD_URL)


def superset_dashboard_url(env_var: str) -> str:
    return os.getenv(env_var, superset_dashboard_fallback_url())


def superset_dashboard_is_configured(url: str) -> bool:
    return "dashboard/list" not in url.rstrip("/")


def superset_dashboard_entries() -> list[dict[str, str | bool]]:
    entries: list[dict[str, str | bool]] = []
    for dashboard in SUPERSET_DASHBOARDS:
        url = superset_dashboard_url(dashboard["env_var"])
        entries.append(
            {
                **dashboard,
                "url": url,
                "configured": superset_dashboard_is_configured(url),
            }
        )
    return entries


def load_model(task_name: str):
    return joblib.load(model_path(task_name))


def score_to_band(score: float | None) -> str | None:
    if score is None:
        return None
    if score >= 0.8:
        return "Cao"
    if score >= 0.55:
        return "Trung b\u00ecnh"
    return "Th\u1ea5p"


def field_label(name: str) -> str:
    return name.replace("_", " ").strip().title()


def field_placeholder(name: str) -> str:
    if name.endswith("_key"):
        return "Nh\u1eadp m\u00e3 \u0111\u1ecbnh danh"
    if "city" in name:
        return "V\u00ed d\u1ee5: Sao Paulo"
    if "state" in name:
        return "V\u00ed d\u1ee5: SP"
    if name.startswith("has_") or name.startswith("uses_"):
        return "Nh\u1eadp True ho\u1eb7c False"
    return "Nh\u1eadp gi\u00e1 tr\u1ecb"


def parse_feature_input(feature_name: str, raw_value: str, numeric: bool):
    if raw_value is None or raw_value.strip() == "":
        raise ValueError(f"Tr\u01b0\u1eddng '{field_label(feature_name)}' ch\u01b0a \u0111\u01b0\u1ee3c nh\u1eadp.")

    cleaned = raw_value.strip()
    if numeric:
        try:
            return float(cleaned)
        except ValueError as exc:
            raise ValueError(f"Tr\u01b0\u1eddng '{field_label(feature_name)}' ph\u1ea3i l\u00e0 s\u1ed1.") from exc

    lowered = cleaned.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    return cleaned


def resolve_prediction_score(model, task, row: pd.DataFrame) -> float | None:
    if task.problem_type != "classification" or not hasattr(model, "predict_proba"):
        return None

    probabilities = model.predict_proba(row)
    classes = list(getattr(model, "classes_", []))
    if task.positive_class_label in classes:
        return float(probabilities[0][classes.index(task.positive_class_label)])
    return float(probabilities[0].max())


def prediction_message(task_name: str, prediction_value) -> str:
    normalized = str(prediction_value).lower()
    positive = normalized in {"true", "1", "yes"}

    if task_name == "product_bestseller":
        return (
            "S\u1ea3n ph\u1ea9m n\u00e0y c\u00f3 kh\u1ea3 n\u0103ng tr\u1edf th\u00e0nh bestseller trong 7 ng\u00e0y t\u1edbi."
            if positive
            else "S\u1ea3n ph\u1ea9m n\u00e0y ch\u01b0a c\u00f3 d\u1ea5u hi\u1ec7u tr\u1edf th\u00e0nh bestseller trong 7 ng\u00e0y t\u1edbi."
        )
    if task_name == "order_success":
        return (
            "\u0110\u01a1n h\u00e0ng n\u00e0y c\u00f3 kh\u1ea3 n\u0103ng giao th\u00e0nh c\u00f4ng."
            if positive
            else "\u0110\u01a1n h\u00e0ng n\u00e0y c\u00f3 r\u1ee7i ro kh\u00f4ng ho\u00e0n t\u1ea5t th\u00e0nh c\u00f4ng."
        )
    return (
        "Khu v\u1ef1c n\u00e0y c\u00f3 kh\u1ea3 n\u0103ng ph\u00e1t sinh nhu c\u1ea7u cao trong 7 ng\u00e0y t\u1edbi."
        if positive
        else "Khu v\u1ef1c n\u00e0y hi\u1ec7n ch\u01b0a c\u00f3 d\u1ea5u hi\u1ec7u nhu c\u1ea7u t\u0103ng cao trong 7 ng\u00e0y t\u1edbi."
    )


def localized_action(task_name: str, band: str | None) -> str:
    actions = {
        "product_bestseller": {
            "Cao": "\u01afu ti\u00ean t\u1ed3n kho, ng\u00e2n s\u00e1ch marketing v\u00e0 n\u0103ng l\u1ef1c s\u1eb5n s\u00e0ng c\u1ee7a nh\u00e0 b\u00e1n cho s\u1ea3n ph\u1ea9m n\u00e0y.",
            "Trung b\u00ecnh": "Theo d\u00f5i xu h\u01b0\u1edbng nhu c\u1ea7u v\u00e0 chu\u1ea9n b\u1ecb h\u1ed7 tr\u1ee3 chi\u1ebfn d\u1ecbch \u1edf m\u1ee9c v\u1eeba ph\u1ea3i.",
            "Th\u1ea5p": "Duy tr\u00ec theo d\u00f5i trong danh m\u1ee5c ti\u00eau chu\u1ea9n.",
        },
        "order_success": {
            "Cao": "Ti\u1ebfp t\u1ee5c lu\u1ed3ng x\u1eed l\u00fd b\u00ecnh th\u01b0\u1eddng v\u00e0 \u01b0u ti\u00ean c\u00e1c \u0111\u01a1n h\u00e0ng gi\u00e1 tr\u1ecb cao.",
            "Trung b\u00ecnh": "R\u00e0 so\u00e1t t\u00edn hi\u1ec7u thanh to\u00e1n v\u00e0 v\u1eadn h\u00e0nh \u0111\u1ec3 b\u1ea3o v\u1ec7 t\u1ef7 l\u1ec7 chuy\u1ec3n \u0111\u1ed5i.",
            "Th\u1ea5p": "G\u1eafn c\u1edd \u0111\u1ec3 \u0111\u1ed9i v\u1eadn h\u00e0nh ki\u1ec3m tra v\u00ec \u0111\u01a1n h\u00e0ng n\u00e0y c\u00f3 nguy c\u01a1 kh\u00f4ng ho\u00e0n t\u1ea5t th\u00e0nh c\u00f4ng.",
        },
        "geo_high_demand": {
            "Cao": "T\u0103ng c\u01b0\u1eddng chi\u1ebfn d\u1ecbch v\u00e0 chu\u1ea9n b\u1ecb n\u0103ng l\u1ef1c logistics cho khu v\u1ef1c n\u00e0y.",
            "Trung b\u00ecnh": "Theo d\u00f5i nhu c\u1ea7u khu v\u1ef1c v\u00e0 chu\u1ea9n b\u1ecb \u01b0u \u0111\u00e3i m\u1ee5c ti\u00eau.",
            "Th\u1ea5p": "Duy tr\u00ec k\u1ebf ho\u1ea1ch khu v\u1ef1c \u1edf m\u1ee9c ti\u00eau chu\u1ea9n.",
        },
    }
    return actions.get(task_name, {}).get(band or "Th\u1ea5p", "Ch\u01b0a c\u00f3 g\u1ee3i \u00fd h\u00e0nh \u0111\u1ed9ng.")


def render_sidebar(ready: bool, message: str) -> None:
    st.sidebar.title("\u0110i\u1ec1u h\u01b0\u1edbng")
    st.sidebar.button("Trang ch\u1ee7", use_container_width=True, on_click=go_to, args=("home", None))
    st.sidebar.button("D\u1ef1 \u0111o\u00e1n", use_container_width=True, on_click=go_to, args=("predict_menu", None))
    st.sidebar.button("Dashboard", use_container_width=True, on_click=go_to, args=("dashboard", None))

    config = db_config()
    st.sidebar.markdown("**C\u01a1 s\u1edf d\u1eef li\u1ec7u**")
    st.sidebar.code(
        f"{config['user']}@{config['host']}:{config['port']}/{config['database']}",
        language="text",
    )

    if ready:
        st.sidebar.success("C\u01a1 s\u1edf d\u1eef li\u1ec7u \u0111ang ho\u1ea1t \u0111\u1ed9ng")
    else:
        st.sidebar.error("C\u01a1 s\u1edf d\u1eef li\u1ec7u \u0111ang ngo\u1ea1i tuy\u1ebfn")
        with st.sidebar.expander("Chi ti\u1ebft l\u1ed7i"):
            st.code(message, language="text")


def render_home(ready: bool, message: str) -> None:
    status_class = "" if ready else " error"
    status_label = (
        "C\u01a1 s\u1edf d\u1eef li\u1ec7u \u0111ang ho\u1ea1t \u0111\u1ed9ng"
        if ready
        else "C\u01a1 s\u1edf d\u1eef li\u1ec7u \u0111ang ngo\u1ea1i tuy\u1ebfn"
    )

    st.markdown(
        f"""
        <div class="hero">
          <span class="status-pill{status_class}">{status_label}</span>
          <h1>E-commerce ML & BI Command Center</h1>
          <p>
            D\u1ef1 \u00e1n khai th\u00e1c b\u1ed9 d\u1eef li\u1ec7u c\u00f4ng khai v\u1ec1 th\u01b0\u01a1ng m\u1ea1i \u0111i\u1ec7n t\u1eed t\u1ea1i Brazil do Olist thu th\u1eadp t\u1eeb h\u1ec7 sinh th\u00e1i marketplace,
            ghi nh\u1eadn kho\u1ea3ng 100.000 \u0111\u01a1n h\u00e0ng giai \u0111o\u1ea1n 2016-2018 c\u00f9ng th\u00f4ng tin v\u1ec1 tr\u1ea1ng th\u00e1i \u0111\u01a1n, gi\u00e1, thanh to\u00e1n, v\u1eadn chuy\u1ec3n, v\u1ecb tr\u00ed kh\u00e1ch h\u00e0ng, thu\u1ed9c t\u00ednh s\u1ea3n ph\u1ea9m v\u00e0 \u0111\u00e1nh gi\u00e1 sau mua.
            T\u1eeb context kinh doanh \u0111\u00f3, h\u1ec7 th\u1ed1ng \u0111\u1ecbnh h\u01b0\u1edbng d\u1eef li\u1ec7u sang ph\u00e2n t\u00edch v\u00e0 h\u1ed7 tr\u1ee3 ra quy\u1ebft \u0111\u1ecbnh theo 3 nghi\u1ec7p v\u1ee5 \u0111\u00e3 th\u1ed1ng nh\u1ea5t:
            d\u1ef1 b\u00e1o s\u1ea3n ph\u1ea9m b\u00e1n ch\u1ea1y, d\u1ef1 b\u00e1o \u0111\u01a1n h\u00e0ng th\u00e0nh c\u00f4ng, v\u00e0 d\u1ef1 b\u00e1o khu v\u1ef1c nhu c\u1ea7u cao \u0111\u1ec3 ph\u1ee5c v\u1ee5 quy\u1ebft \u0111\u1ecbnh t\u1ed3n kho, marketing v\u00e0 v\u1eadn h\u00e0nh.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not ready:
        st.warning("Ch\u01b0a k\u1ebft n\u1ed1i \u0111\u01b0\u1ee3c Postgres. App v\u1eabn m\u1edf \u0111\u01b0\u1ee3c, nh\u01b0ng dashboard v\u00e0 d\u1ef1 \u0111o\u00e1n s\u1ebd kh\u00f4ng ch\u1ea1y \u0111\u1ea7y \u0111\u1ee7.")
        st.code(message, language="text")

    st.markdown('<div class="section-title">B\u1eaft \u0111\u1ea7u</div>', unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        st.markdown(
            """
            <div class="nav-card">
              <div class="label">D\u1ef1 \u0111o\u00e1n</div>
              <div class="value">Machine Learning</div>
              <div class="hint">M\u00f4 ph\u1ecfng 3 b\u00e0i to\u00e1n nghi\u1ec7p v\u1ee5 c\u1ed1t l\u00f5i: s\u1ea3n ph\u1ea9m n\u00e0o s\u1eafp b\u00e1n ch\u1ea1y, \u0111\u01a1n h\u00e0ng n\u00e0o c\u00f3 nguy c\u01a1 kh\u00f4ng th\u00e0nh c\u00f4ng, v\u00e0 khu v\u1ef1c n\u00e0o s\u1eafp t\u0103ng nhu c\u1ea7u.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("M\u1edf khu v\u1ef1c d\u1ef1 \u0111o\u00e1n", use_container_width=True, on_click=go_to, args=("predict_menu", None))

    with right:
        st.markdown(
            """
            <div class="nav-card">
              <div class="label">Dashboard</div>
              <div class="value">T\u1ed5ng quan kinh doanh</div>
              <div class="hint">Theo d\u00f5i KPI, doanh thu, thanh to\u00e1n, \u0111\u00e1nh gi\u00e1 kh\u00e1ch h\u00e0ng v\u00e0 c\u00e1c t\u00edn hi\u1ec7u d\u1ef1 b\u00e1o \u0111\u1ec3 ph\u1ee5c v\u1ee5 quy\u1ebft \u0111\u1ecbnh kinh doanh tr\u00ean d\u1eef li\u1ec7u Olist.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("M\u1edf dashboard", use_container_width=True, on_click=go_to, args=("dashboard", None))


def render_predict_menu() -> None:
    st.markdown(
        """
        <div class="hero compact">
          <h1>Ch\u1ecdn Nghi\u1ec7p V\u1ee5 D\u1ef1 \u0110o\u00e1n</h1>
          <p>M\u1ed7i b\u00e0i to\u00e1n t\u01b0\u01a1ng \u1ee9ng v\u1edbi m\u1ed9t quy\u1ebft \u0111\u1ecbnh nghi\u1ec7p v\u1ee5 th\u1ef1c t\u1ebf trong th\u01b0\u01a1ng m\u1ea1i \u0111i\u1ec7n t\u1eed: \u01b0u ti\u00ean t\u1ed3n kho, can thi\u1ec7p \u0111\u01a1n h\u00e0ng r\u1ee7i ro, ho\u1eb7c chu\u1ea9n b\u1ecb campaign/logistics theo khu v\u1ef1c.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.button("Quay l\u1ea1i trang ch\u1ee7", on_click=go_to, args=("home", None))

    st.markdown('<div class="section-title">Danh s\u00e1ch b\u00e0i to\u00e1n</div>', unsafe_allow_html=True)
    columns = st.columns(3)
    for column, item in zip(columns, BUSINESS_TASKS):
        with column:
            st.markdown(
                f"""
                <div class="task-card">
                  <div class="label">{item["label"]}</div>
                  <div class="hint">{item["caption"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(
                f"Ch\u1ecdn {item['label']}",
                key=f"nav_{item['task_name']}",
                use_container_width=True,
                on_click=go_to,
                args=("predict_form", item["task_name"]),
            )


def render_dashboard(ready: bool, message: str) -> None:
    dashboard_entries = superset_dashboard_entries()
    has_unconfigured_dashboard = any(not entry["configured"] for entry in dashboard_entries)

    st.markdown(
        """
        <div class="hero compact">
          <h1>BI Dashboard</h1>
          <p>Trang này là hub mở nhanh 3 dashboard Superset riêng cho 3 use case ML.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.button("Quay l\u1ea1i trang ch\u1ee7", on_click=go_to, args=("home", None))
    if not ready:
        st.warning("Cơ sở dữ liệu đang ngoại tuyến. Bạn vẫn có thể mở dashboard nếu Superset và Postgres còn truy cập được.")
        st.code(message, language="text")

    st.markdown('<div class="section-title">Danh sách dashboard</div>', unsafe_allow_html=True)
    columns = st.columns(3)
    for column, entry in zip(columns, dashboard_entries):
        with column:
            st.markdown(
                f"""
                <div class="nav-card">
                  <div class="label">{entry["label"]}</div>
                  <div class="hint">{entry["caption"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.link_button(
                f"Mở {entry['label']}",
                str(entry["url"]),
                use_container_width=True,
            )
            if entry["configured"]:
                st.caption("Đã cấu hình link dashboard riêng.")
            else:
                st.caption(f"Chưa cấu hình `{entry['env_var']}`, đang fallback sang dashboard list.")

    if has_unconfigured_dashboard:
        st.info(
            "Để từng nút mở đúng dashboard riêng trong Superset, hãy cập nhật các biến môi trường "
            "`SUPERSET_PRODUCT_BESTSELLER_DASHBOARD_URL`, "
            "`SUPERSET_ORDER_SUCCESS_DASHBOARD_URL`, "
            "`SUPERSET_GEO_DEMAND_DASHBOARD_URL`."
        )

def render_prediction_result(task_name: str, prediction_value, prediction_score: float | None) -> None:
    band = score_to_band(prediction_score)
    action = localized_action(task_name, band)
    title = prediction_message(task_name, prediction_value)

    if band == "Cao":
        st.success(f"K\u1ebft qu\u1ea3 d\u1ef1 \u0111o\u00e1n: {title}")
    elif band == "Trung b\u00ecnh":
        st.warning(f"K\u1ebft qu\u1ea3 d\u1ef1 \u0111o\u00e1n: {title}")
    else:
        st.info(f"K\u1ebft qu\u1ea3 d\u1ef1 \u0111o\u00e1n: {title}")

    left, right, extra = st.columns(3)
    left.metric("Prediction", str(prediction_value))
    right.metric("\u0110\u1ed9 tin c\u1eady", "-" if prediction_score is None else f"{prediction_score:.2%}")
    extra.metric("M\u1ee9c \u0111\u1ed9", band or "-")

    st.markdown(
        f"""
        <div class="soft-note">
          <b>G\u1ee3i \u00fd h\u00e0nh \u0111\u1ed9ng:</b> {action}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_predict_form(ready: bool, message: str, task_name: str | None) -> None:
    if not task_name:
        redirect("predict_menu", None)
        return

    task = get_task(task_name)
    st.markdown(
        f"""
        <div class="hero compact">
          <h1>{TASK_LABELS[task_name]}</h1>
          <p>{TASK_CAPTIONS[task_name]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    back_col, home_col = st.columns(2)
    back_col.button("Quay l\u1ea1i danh s\u00e1ch nghi\u1ec7p v\u1ee5", on_click=go_to, args=("predict_menu", None), use_container_width=True)
    home_col.button("V\u1ec1 trang ch\u1ee7", on_click=go_to, args=("home", None), use_container_width=True)

    st.markdown('<div class="section-title">M\u00f4 t\u1ea3 b\u00e0i to\u00e1n</div>', unsafe_allow_html=True)
    st.write(TASK_GOALS[task_name])
    st.caption("C\u00e2u h\u1ecfi m\u1eabu: " + " | ".join(TASK_QUESTIONS[task_name]))

    if not ready:
        st.warning("C\u01a1 s\u1edf d\u1eef li\u1ec7u \u0111ang ngo\u1ea1i tuy\u1ebfn. B\u1ea1n v\u1eabn c\u00f3 th\u1ec3 d\u1ef1 \u0111o\u00e1n th\u1ee7 c\u00f4ng n\u1ebfu artifact model \u0111\u00e3 \u0111\u01b0\u1ee3c train s\u1eb5n.")

    if not model_path(task_name).exists():
        st.warning("Ch\u01b0a c\u00f3 model artifact cho b\u00e0i to\u00e1n n\u00e0y. H\u00e3y train tr\u01b0\u1edbc b\u1eb1ng Airflow ho\u1eb7c CLI.")
        return

    if metadata_path(task_name).exists():
        metadata = json.loads(metadata_path(task_name).read_text(encoding="utf-8"))
        metric_values = metadata.get("metrics", {})
        if isinstance(metric_values, dict) and metric_values:
            st.markdown('<div class="section-title">Ch\u1ec9 s\u1ed1 hu\u1ea5n luy\u1ec7n</div>', unsafe_allow_html=True)
            metric_cols = st.columns(len(metric_values))
            for col, (name, value) in zip(metric_cols, metric_values.items()):
                col.metric(name, f"{float(value):.4f}")

    st.markdown('<div class="section-title">Nh\u1eadp d\u1eef li\u1ec7u d\u1ef1 \u0111o\u00e1n</div>', unsafe_allow_html=True)
    st.caption("Nh\u1eadp \u0111\u1ea7y \u0111\u1ee7 c\u00e1c tr\u01b0\u1eddng d\u1eef li\u1ec7u, sau \u0111\u00f3 nh\u1ea5n G\u1eedi d\u1ef1 \u0111o\u00e1n \u0111\u1ec3 nh\u1eadn k\u1ebft qu\u1ea3.")

    feature_values: dict[str, object] = {}
    form_key = f"predict_form_{task_name}"
    with st.form(form_key):
        st.markdown("**Th\u00f4ng tin \u0111\u1ecbnh t\u00ednh**")
        categorical_columns = st.columns(2)
        for index, feature_name in enumerate(task.categorical_features):
            with categorical_columns[index % 2]:
                raw_value = st.text_input(
                    field_label(feature_name),
                    key=f"{form_key}_{feature_name}",
                    placeholder=field_placeholder(feature_name),
                )
                feature_values[feature_name] = raw_value

        st.markdown("**Th\u00f4ng tin s\u1ed1 h\u1ecdc**")
        numeric_columns = st.columns(2)
        for index, feature_name in enumerate(task.numeric_features):
            with numeric_columns[index % 2]:
                raw_value = st.text_input(
                    field_label(feature_name),
                    key=f"{form_key}_{feature_name}",
                    placeholder=field_placeholder(feature_name),
                )
                feature_values[feature_name] = raw_value

        submitted = st.form_submit_button("G\u1eedi d\u1ef1 \u0111o\u00e1n")

    if not submitted:
        return

    try:
        parsed_row = {}
        for feature_name in task.categorical_features:
            parsed_row[feature_name] = parse_feature_input(
                feature_name,
                str(feature_values[feature_name]),
                numeric=False,
            )
        for feature_name in task.numeric_features:
            parsed_row[feature_name] = parse_feature_input(
                feature_name,
                str(feature_values[feature_name]),
                numeric=True,
            )

        model = load_model(task_name)
        inference_row = pd.DataFrame([parsed_row], columns=task.numeric_features + task.categorical_features)
        prediction_value = model.predict(inference_row)[0]
        prediction_score = resolve_prediction_score(model, task, inference_row)
        render_prediction_result(task_name, prediction_value, prediction_score)
    except Exception as exc:
        st.error("Kh\u00f4ng th\u1ec3 t\u1ea1o d\u1ef1 \u0111o\u00e1n t\u1eeb d\u1eef li\u1ec7u v\u1eeba nh\u1eadp.")
        st.code(str(exc), language="text")


load_css()
init_state()

ready, message = database_is_ready()
render_sidebar(ready, message)

view = st.session_state["view"]
selected_task = st.session_state["selected_task"]

if view == "dashboard":
    render_dashboard(ready, message)
elif view == "predict_menu":
    render_predict_menu()
elif view == "predict_form":
    render_predict_form(ready, message, selected_task)
else:
    render_home(ready, message)
