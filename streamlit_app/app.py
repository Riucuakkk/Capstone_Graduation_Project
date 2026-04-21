from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.db_connection import database_is_ready, db_config


st.set_page_config(
    page_title="E-commerce ML & BI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css() -> None:
    css_path = Path(__file__).parent / "assets" / "style.css"
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


load_css()

ready, message = database_is_ready()
status_class = "" if ready else " error"
status_label = "Database online" if ready else "Database offline"

st.markdown(
    f"""
    <div class="hero">
      <span class="status-pill{status_class}">{status_label}</span>
      <h1>E-commerce ML & BI Command Center</h1>
      <p>
        Theo doi doanh thu, van hanh giao hang, chat luong review va cac bai toan
        machine learning tren data mart Olist trong mot giao dien Streamlit gon, dep va de trinh bay.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("E-commerce Analytics")
st.sidebar.caption("BI dashboards, ML catalog, predictions")

config = db_config()
st.sidebar.markdown("**Database**")
st.sidebar.code(
    f"{config['user']}@{config['host']}:{config['port']}/{config['database']}",
    language="text",
)

if not ready:
    st.warning("Chua ket noi duoc Postgres. Hay chay pipeline/dbt truoc, hoac kiem tra bien moi truong DB_HOST, DB_PORT.")
    with st.expander("Chi tiet loi ket noi"):
        st.code(message, language="text")
else:
    st.success("Da ket noi Postgres. Mo sidebar Pages de xem dashboard BI, ML Predict va Forecast.")

st.markdown('<div class="section-title">Cac vung chuc nang</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="metric-card">
          <div class="label">BI Overview</div>
          <div class="value">Sales</div>
          <div class="hint">Doanh thu, don hang, thanh toan, review va category performance.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="metric-card">
          <div class="label">Machine Learning</div>
          <div class="value">Risk</div>
          <div class="hint">Late delivery, low review, seller risk, customer value va order value.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="metric-card">
          <div class="label">Forecast</div>
          <div class="value">Demand</div>
          <div class="hint">Xu huong doanh thu/category theo ngay va tin hieu lap ke hoach.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="soft-note">
      Ung dung doc truc tiep schema <b>marts</b> tu PostgreSQL. Neu mot bang mart chua ton tai,
      trang lien quan se hien thong bao nhe thay vi lam sap app.
    </div>
    """,
    unsafe_allow_html=True,
)
