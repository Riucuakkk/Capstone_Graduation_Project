from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from streamlit_app.components.charts import bar_chart, line_chart
from streamlit_app.components.db_connection import database_is_ready, read_sql


st.set_page_config(page_title="Demand Forecast", page_icon="🔮", layout="wide")


def load_css() -> None:
    css_path = Path(__file__).resolve().parents[1] / "assets" / "style.css"
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def run_query(sql: str, params: tuple | None = None) -> pd.DataFrame:
    try:
        return read_sql(sql, params=params)
    except Exception as exc:
        st.info(f"Chua doc duoc du lieu forecast: {exc}")
        return pd.DataFrame()


load_css()
st.title("Demand & Revenue Forecast")
st.caption("Theo doi chuoi thoi gian category va dau vao cho bai toan daily_category_revenue_regression.")

ready, message = database_is_ready()
if not ready:
    st.error("Postgres chua san sang.")
    st.code(message, language="text")
    st.stop()

category_sql = """
select
    entity_key,
    sum(total_revenue)::numeric as revenue
from marts.fact_demand_series
where entity_type = 'category'
group by 1
order by revenue desc
limit 30
"""
categories = run_query(category_sql)
if categories.empty:
    st.stop()

selected = st.selectbox("Category", categories["entity_key"].tolist())

series_sql = """
select
    full_date,
    total_orders,
    total_units,
    total_revenue,
    avg(total_revenue) over (
        partition by entity_key
        order by full_date
        rows between 6 preceding and current row
    ) as trailing_7d_avg_revenue
from marts.fact_demand_series
where entity_type = 'category'
  and entity_key = %s
order by full_date
"""
series = run_query(series_sql, (selected,))

if series.empty:
    st.warning("Khong co series cho category da chon.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Revenue", f"${float(series['total_revenue'].sum()):,.0f}")
col2.metric("Orders", f"{int(series['total_orders'].sum()):,}")
col3.metric("Units", f"{int(series['total_units'].sum()):,}")

chart_df = series.melt(
    id_vars=["full_date"],
    value_vars=["total_revenue", "trailing_7d_avg_revenue"],
    var_name="metric",
    value_name="value",
)
st.plotly_chart(line_chart(chart_df, "full_date", "value", "Revenue trend and 7-day trailing average", "metric"), use_container_width=True)

st.markdown('<div class="section-title">Top Demand Signals</div>', unsafe_allow_html=True)
top = categories.head(12).rename(columns={"entity_key": "category"})
st.plotly_chart(bar_chart(top, "category", "revenue", "Top categories by historical revenue"), use_container_width=True)

st.dataframe(series.tail(60).sort_values("full_date", ascending=False), use_container_width=True, hide_index=True)
