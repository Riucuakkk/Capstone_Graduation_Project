from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from streamlit_app.components.charts import bar_chart, donut_chart, line_chart
from streamlit_app.components.db_connection import database_is_ready, read_sql


st.set_page_config(page_title="BI Dashboard", page_icon="📈", layout="wide")


def load_css() -> None:
    css_path = Path(__file__).resolve().parents[1] / "assets" / "style.css"
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def run_query(sql: str, fallback: pd.DataFrame | None = None) -> pd.DataFrame:
    try:
        return read_sql(sql)
    except Exception as exc:
        st.info(f"Chua doc duoc du lieu mart: {exc}")
        return fallback if fallback is not None else pd.DataFrame()


load_css()
st.title("BI Dashboard")
st.caption("Tong quan kinh doanh tu cac bang marts cua Olist e-commerce.")

ready, message = database_is_ready()
if not ready:
    st.error("Postgres chua san sang.")
    st.code(message, language="text")
    st.stop()

kpi_sql = """
select
    count(*)::int as total_orders,
    coalesce(sum(total_payment_value), 0)::numeric as revenue,
    coalesce(avg(total_payment_value), 0)::numeric as avg_order_value,
    coalesce(avg(approval_lead_hours), 0)::numeric as avg_approval_hours
from marts.fact_orders
"""
kpi = run_query(kpi_sql)

if kpi.empty:
    st.stop()

row = kpi.iloc[0]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Orders", f"{int(row['total_orders']):,}")
col2.metric("Revenue", f"${float(row['revenue']):,.0f}")
col3.metric("AOV", f"${float(row['avg_order_value']):,.2f}")
col4.metric("Approval Hours", f"{float(row['avg_approval_hours']):.1f}")

daily_sql = """
select
    order_purchase_timestamp::date as order_date,
    count(*)::int as orders,
    sum(total_payment_value)::numeric as revenue
from marts.fact_orders
where order_purchase_timestamp is not null
group by 1
order by 1
"""
payment_sql = """
select
    coalesce(dominant_payment_type, 'unknown') as payment_type,
    count(*)::int as orders,
    sum(total_payment_value)::numeric as revenue
from marts.fact_orders
group by 1
order by revenue desc
limit 8
"""
review_sql = """
select
    review_score,
    count(*)::int as reviews
from marts.fact_reviews
where review_score is not null
group by 1
order by 1
"""
category_sql = """
select
    coalesce(category_name_english, entity_key) as category,
    sum(total_revenue)::numeric as revenue,
    sum(total_orders)::int as orders
from marts.fact_demand_series f
left join marts.dim_product_category d
    on f.entity_key = d.product_category_key
where f.entity_type = 'category'
group by 1
order by revenue desc
limit 12
"""

daily = run_query(daily_sql)
payments = run_query(payment_sql)
reviews = run_query(review_sql)
categories = run_query(category_sql)

left, right = st.columns((2, 1))
with left:
    if not daily.empty:
        st.plotly_chart(line_chart(daily, "order_date", "revenue", "Revenue by order date"), use_container_width=True)
with right:
    if not payments.empty:
        st.plotly_chart(donut_chart(payments, "payment_type", "revenue", "Revenue mix by payment"), use_container_width=True)

left, right = st.columns(2)
with left:
    if not categories.empty:
        st.plotly_chart(bar_chart(categories, "category", "revenue", "Top categories by revenue"), use_container_width=True)
with right:
    if not reviews.empty:
        st.plotly_chart(bar_chart(reviews, "review_score", "reviews", "Review score distribution"), use_container_width=True)

st.markdown('<div class="section-title">Recent Orders</div>', unsafe_allow_html=True)
recent_sql = """
select
    order_key,
    order_purchase_timestamp,
    total_items,
    total_payment_value,
    dominant_payment_type,
    approval_lead_hours
from marts.fact_orders
order by order_purchase_timestamp desc nulls last
limit 50
"""
recent = run_query(recent_sql)
if not recent.empty:
    st.dataframe(recent, use_container_width=True, hide_index=True)
