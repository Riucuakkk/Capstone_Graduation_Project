from __future__ import annotations

from dataclasses import dataclass


# Cau hinh 1 bai toan ML: SQL lay du lieu, cot target, feature va y nghia nghiep vu.
@dataclass(frozen=True)
class TaskConfig:
    name: str
    problem_type: str
    entity_name: str
    prediction_name: str
    business_goal: str
    source_sql: str
    target_column: str
    id_columns: list[str]
    numeric_features: list[str]
    categorical_features: list[str]
    where_clause: str = ""
    time_column: str | None = None
    positive_class_label: str | bool | int | None = None
    lower_is_riskier: bool = False
    example_questions: tuple[str, ...] = ()


# Catalog cac bai toan ML dung chung cho train/predict.
TASKS: dict[str, TaskConfig] = {
    # Nghiep vu giao van: du doan line item co nguy co giao tre.
    "late_delivery": TaskConfig(
        name="late_delivery",
        problem_type="classification",
        entity_name="order_item",
        prediction_name="late_delivery_risk",
        business_goal="Predict whether an order item is likely to be delivered late.",
        source_sql="""
            select
                order_item_key,
                order_id,
                snapshot_date,
                customer_key,
                product_key,
                seller_key,
                price,
                freight_value,
                gross_item_amount,
                product_weight_g,
                product_length_cm,
                product_height_cm,
                product_width_cm,
                approval_lead_hours,
                is_delivered_late
            from marts.fact_delivery_line_snapshot
        """,
        target_column="is_delivered_late",
        id_columns=["order_item_key", "order_id"],
        numeric_features=[
            "price",
            "freight_value",
            "gross_item_amount",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
            "approval_lead_hours",
        ],
        categorical_features=[
            "customer_key",
            "product_key",
            "seller_key",
        ],
        where_clause="where is_delivered_late is not null",
        time_column="snapshot_date",
        positive_class_label=True,
        example_questions=(
            "Don hang nao co nguy co giao tre cao?",
            "Line item nao can uu tien theo doi SLA?",
        ),
    ),
    # Nghiep vu cham soc khach hang: du doan order co nguy co nhan review thap.
    "low_review": TaskConfig(
        name="low_review",
        problem_type="classification",
        entity_name="order",
        prediction_name="low_review_risk",
        business_goal="Predict whether an order is likely to receive a low review score.",
        source_sql="""
            select
                order_key,
                snapshot_date,
                customer_key,
                total_items,
                distinct_products,
                distinct_sellers,
                total_item_price,
                total_freight_value,
                total_gross_amount,
                total_payment_value,
                max_payment_installments,
                has_installments,
                is_low_review_order
            from marts.fact_order_snapshot_ml
        """,
        target_column="is_low_review_order",
        id_columns=["order_key"],
        numeric_features=[
            "total_items",
            "distinct_products",
            "distinct_sellers",
            "total_item_price",
            "total_freight_value",
            "total_gross_amount",
            "total_payment_value",
            "max_payment_installments",
        ],
        categorical_features=[
            "customer_key",
            "has_installments",
        ],
        where_clause="where is_low_review_order is not null",
        time_column="snapshot_date",
        positive_class_label=True,
        example_questions=(
            "Don nao co nguy co bi review thap?",
            "Order nao can cham soc khach hang som?",
        ),
    ),
    # Nghiep vu CRM/marketing: du doan nhom gia tri cua khach hang o don tiep theo.
    "customer_value_tier": TaskConfig(
        name="customer_value_tier",
        problem_type="classification",
        entity_name="customer",
        prediction_name="customer_value_segment",
        business_goal="Predict the next-order customer value tier from current customer history.",
        source_sql="""
            with customer_history as (
                select
                    customer_key,
                    snapshot_date,
                    order_sequence_number,
                    cumulative_orders,
                    cumulative_revenue,
                    cumulative_avg_order_value,
                    cumulative_avg_review_score,
                    cumulative_late_delivery_ratio,
                    days_since_previous_order,
                    lead(cumulative_revenue) over (
                        partition by customer_key
                        order by snapshot_date, anchor_order_key
                    ) as next_cumulative_revenue
                from marts.fact_customer_snapshot
            )
            select
                customer_key,
                snapshot_date,
                order_sequence_number,
                cumulative_orders,
                cumulative_revenue,
                cumulative_avg_order_value,
                cumulative_avg_review_score,
                cumulative_late_delivery_ratio,
                days_since_previous_order,
                case
                    when next_cumulative_revenue >= 1000 then 'high'
                    when next_cumulative_revenue >= 300 then 'medium'
                    when next_cumulative_revenue is not null then 'low'
                end as customer_value_segment
            from customer_history
        """,
        target_column="customer_value_segment",
        id_columns=["customer_key"],
        numeric_features=[
            "order_sequence_number",
            "cumulative_orders",
            "cumulative_revenue",
            "cumulative_avg_order_value",
            "cumulative_avg_review_score",
            "cumulative_late_delivery_ratio",
            "days_since_previous_order",
        ],
        categorical_features=[],
        where_clause="where customer_value_segment is not null",
        time_column="snapshot_date",
        positive_class_label="high",
        example_questions=(
            "Khach hang nay o don tiep theo thuoc nhom gia tri nao?",
            "Tap khach nao co kha nang tro thanh high value customer?",
        ),
    ),
    # Nghiep vu giao van: uoc tinh so ngay giao hang cua tung order item.
    "delivery_days_regression": TaskConfig(
        name="delivery_days_regression",
        problem_type="regression",
        entity_name="order_item",
        prediction_name="predicted_delivery_days",
        business_goal="Estimate delivery cycle in days for each order item.",
        source_sql="""
            select
                order_item_key,
                order_id,
                snapshot_date,
                customer_key,
                product_key,
                seller_key,
                price,
                freight_value,
                gross_item_amount,
                product_weight_g,
                product_length_cm,
                product_height_cm,
                product_width_cm,
                approval_lead_hours,
                delivery_cycle_days
            from marts.fact_delivery_line_snapshot
        """,
        target_column="delivery_cycle_days",
        id_columns=["order_item_key", "order_id"],
        numeric_features=[
            "price",
            "freight_value",
            "gross_item_amount",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
            "approval_lead_hours",
        ],
        categorical_features=[
            "customer_key",
            "product_key",
            "seller_key",
        ],
        where_clause="where delivery_cycle_days is not null",
        time_column="snapshot_date",
        lower_is_riskier=False,
        example_questions=(
            "Mat bao nhieu ngay de giao line item nay?",
            "Du kien thoi gian giao hang cua don nay la bao lau?",
        ),
    ),
    # Nghiep vu doanh thu: uoc tinh gia tri thanh toan cua order.
    "order_value_regression": TaskConfig(
        name="order_value_regression",
        problem_type="regression",
        entity_name="order",
        prediction_name="predicted_order_value",
        business_goal="Estimate order value from order structure and payment behavior.",
        source_sql="""
            select
                order_key,
                order_purchase_timestamp::date as order_date,
                customer_key,
                total_items,
                distinct_products,
                distinct_sellers,
                total_item_price,
                total_freight_value,
                max_payment_installments,
                has_installments,
                uses_credit_card,
                uses_voucher,
                dominant_payment_type,
                approval_lead_hours,
                total_payment_value
            from marts.fact_orders
        """,
        target_column="total_payment_value",
        id_columns=["order_key"],
        numeric_features=[
            "total_items",
            "distinct_products",
            "distinct_sellers",
            "total_item_price",
            "total_freight_value",
            "max_payment_installments",
            "approval_lead_hours",
        ],
        categorical_features=[
            "customer_key",
            "has_installments",
            "uses_credit_card",
            "uses_voucher",
            "dominant_payment_type",
        ],
        where_clause="where total_payment_value is not null",
        time_column="order_date",
        example_questions=(
            "Don hang nay du kien gia tri bao nhieu?",
            "Order nao co kha nang mang lai doanh thu cao?",
        ),
    ),
    # Nghiep vu van hanh seller: du doan muc rui ro cua seller trong ngay tiep theo.
    "seller_risk_band": TaskConfig(
        name="seller_risk_band",
        problem_type="classification",
        entity_name="seller_day",
        prediction_name="seller_next_day_operational_risk",
        business_goal="Predict next-day seller operational risk from recent seller activity.",
        source_sql="""
            with seller_daily as (
                select
                    fsd.seller_key,
                    fsd.full_date,
                    ds.seller_state,
                    fsd.total_orders,
                    fsd.total_items,
                    fsd.total_gross_amount,
                    fsd.total_freight_value,
                    fsd.shipped_after_limit_ratio,
                    fsd.delivered_late_ratio,
                    lag(fsd.total_orders, 1) over (
                        partition by fsd.seller_key
                        order by fsd.full_date
                    ) as lag_1_total_orders,
                    lag(fsd.total_items, 1) over (
                        partition by fsd.seller_key
                        order by fsd.full_date
                    ) as lag_1_total_items,
                    lag(fsd.total_gross_amount, 1) over (
                        partition by fsd.seller_key
                        order by fsd.full_date
                    ) as lag_1_total_gross_amount,
                    lag(fsd.shipped_after_limit_ratio, 1) over (
                        partition by fsd.seller_key
                        order by fsd.full_date
                    ) as lag_1_shipped_after_limit_ratio,
                    lag(fsd.delivered_late_ratio, 1) over (
                        partition by fsd.seller_key
                        order by fsd.full_date
                    ) as lag_1_delivered_late_ratio,
                    lead(fsd.delivered_late_ratio, 1) over (
                        partition by fsd.seller_key
                        order by fsd.full_date
                    ) as next_delivered_late_ratio
                from marts.fact_seller_daily fsd
                left join marts.dim_sellers ds
                    on fsd.seller_key = ds.seller_key
            )
            select
                seller_key,
                full_date,
                seller_state,
                total_orders,
                total_items,
                total_gross_amount,
                total_freight_value,
                shipped_after_limit_ratio,
                delivered_late_ratio,
                lag_1_total_orders,
                lag_1_total_items,
                lag_1_total_gross_amount,
                lag_1_shipped_after_limit_ratio,
                lag_1_delivered_late_ratio,
                case
                    when next_delivered_late_ratio >= 0.3 then 'high_risk'
                    when next_delivered_late_ratio >= 0.15 then 'medium_risk'
                    when next_delivered_late_ratio is not null then 'low_risk'
                end as seller_risk_band
            from seller_daily
        """,
        target_column="seller_risk_band",
        id_columns=["seller_key", "full_date"],
        numeric_features=[
            "total_orders",
            "total_items",
            "total_gross_amount",
            "total_freight_value",
            "shipped_after_limit_ratio",
            "delivered_late_ratio",
            "lag_1_total_orders",
            "lag_1_total_items",
            "lag_1_total_gross_amount",
            "lag_1_shipped_after_limit_ratio",
            "lag_1_delivered_late_ratio",
        ],
        categorical_features=["seller_state"],
        where_clause="where seller_risk_band is not null",
        time_column="full_date",
        positive_class_label="high_risk",
        example_questions=(
            "Seller nao dang co rui ro van hanh cao?",
            "Nen uu tien theo doi seller nao?",
        ),
    ),
    # Nghiep vu demand planning: du bao doanh thu ngay tiep theo theo category.
    "daily_category_revenue_regression": TaskConfig(
        name="daily_category_revenue_regression",
        problem_type="regression",
        entity_name="category_day",
        prediction_name="predicted_daily_category_revenue",
        business_goal="Estimate daily category revenue for demand planning.",
        source_sql="""
            with demand_series as (
                select
                    entity_key,
                    full_date,
                    date_key,
                    extract(month from full_date) as calendar_month,
                    extract(day from full_date) as calendar_day,
                    extract(isodow from full_date) as iso_weekday,
                    total_orders,
                    total_units,
                    total_revenue,
                    lag(total_orders, 1) over (
                        partition by entity_key
                        order by full_date
                    ) as lag_1_total_orders,
                    lag(total_units, 1) over (
                        partition by entity_key
                        order by full_date
                    ) as lag_1_total_units,
                    lag(total_revenue, 1) over (
                        partition by entity_key
                        order by full_date
                    ) as lag_1_total_revenue,
                    lag(total_revenue, 7) over (
                        partition by entity_key
                        order by full_date
                    ) as lag_7_total_revenue,
                    avg(total_revenue) over (
                        partition by entity_key
                        order by full_date
                        rows between 6 preceding and current row
                    ) as trailing_7d_avg_revenue,
                    lead(total_revenue, 1) over (
                        partition by entity_key
                        order by full_date
                    ) as next_day_revenue
                from marts.fact_demand_series
                where entity_type = 'category'
            )
            select
                entity_key,
                full_date,
                date_key,
                calendar_month,
                calendar_day,
                iso_weekday,
                total_orders,
                total_units,
                lag_1_total_orders,
                lag_1_total_units,
                lag_1_total_revenue,
                lag_7_total_revenue,
                trailing_7d_avg_revenue,
                next_day_revenue as total_revenue
            from demand_series
        """,
        target_column="total_revenue",
        id_columns=["entity_key", "date_key"],
        numeric_features=[
            "calendar_month",
            "calendar_day",
            "iso_weekday",
            "total_orders",
            "total_units",
            "lag_1_total_orders",
            "lag_1_total_units",
            "lag_1_total_revenue",
            "lag_7_total_revenue",
            "trailing_7d_avg_revenue",
        ],
        categorical_features=["entity_key"],
        where_clause="where total_revenue is not null",
        time_column="full_date",
        example_questions=(
            "Doanh thu category ngay mai du kien bao nhieu?",
            "Category nao sap tang truong doanh thu?",
        ),
    ),
}


# Lay 1 task theo ten de CLI/API khong phai truy cap truc tiep dictionary.
def get_task(task_name: str) -> TaskConfig:
    if task_name not in TASKS:
        supported = ", ".join(sorted(TASKS))
        raise ValueError(f"Unsupported task '{task_name}'. Supported tasks: {supported}")
    return TASKS[task_name]


# Liet ke task theo thu tu on dinh de hien thi catalog.
def list_tasks() -> list[TaskConfig]:
    return [TASKS[name] for name in sorted(TASKS)]
