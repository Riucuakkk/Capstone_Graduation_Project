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


st.set_page_config(page_title="Product Demand", layout="wide")


def load_css() -> None:
    css_path = Path(__file__).resolve().parents[1] / "assets" / "style.css"
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def run_query(sql: str, params: tuple | None = None) -> pd.DataFrame:
    try:
        return read_sql(sql, params=params)
    except Exception as exc:
        st.info(f"Chua doc duoc du lieu demand ML: {exc}")
        return pd.DataFrame()


load_css()
st.title("Product Demand")
st.caption("Theo doi tin hieu san pham ban chay tu mart `fact_ml_product_demand`.")

ready, message = database_is_ready()
if not ready:
    st.error("Postgres chua san sang.")
    st.code(message, language="text")
    st.stop()

product_sql = """
select
    product_key,
    product_category,
    sum(total_items)::numeric as historical_units,
    sum(total_gross_amount)::numeric as historical_revenue,
    sum(next_7d_units)::numeric as next_7d_units_signal,
    max(case when is_bestseller_next_7d then 1 else 0 end) as has_bestseller_signal
from marts.fact_ml_product_demand
group by 1, 2
order by next_7d_units_signal desc, historical_revenue desc
limit 50
"""
products = run_query(product_sql)
if products.empty:
    st.stop()

products["label"] = products["product_category"].fillna("unknown") + " | " + products["product_key"].astype(str)
selected_label = st.selectbox("Product", products["label"].tolist())
selected_product = products.loc[products["label"] == selected_label, "product_key"].iloc[0]

series_sql = """
select
    full_date,
    product_category,
    total_items,
    total_orders,
    total_gross_amount,
    trailing_7_sale_day_avg_items,
    trailing_7_sale_day_avg_revenue,
    next_7d_units,
    next_7d_revenue,
    is_bestseller_next_7d
from marts.fact_ml_product_demand
where product_key = %s
order by full_date
"""
series = run_query(series_sql, (selected_product,))

if series.empty:
    st.warning("Khong co series cho san pham da chon.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Historical units", f"{int(series['total_items'].sum()):,}")
col2.metric("Historical revenue", f"${float(series['total_gross_amount'].sum()):,.0f}")
col3.metric("Next 7d unit signal", f"{int(series['next_7d_units'].sum()):,}")

chart_df = series.melt(
    id_vars=["full_date"],
    value_vars=["total_items", "trailing_7_sale_day_avg_items", "next_7d_units"],
    var_name="metric",
    value_name="value",
)
st.plotly_chart(
    line_chart(chart_df, "full_date", "value", "Product demand signals", "metric"),
    use_container_width=True,
)

st.markdown('<div class="section-title">Top Product Signals</div>', unsafe_allow_html=True)
top = products.head(12).rename(columns={"label": "product"})
st.plotly_chart(
    bar_chart(top, "product", "next_7d_units_signal", "Top products by next-7-day demand signal"),
    use_container_width=True,
)

st.dataframe(series.tail(60).sort_values("full_date", ascending=False), use_container_width=True, hide_index=True)
