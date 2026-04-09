from dataclasses import dataclass


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
    positive_class_label: str | None = None
    lower_is_riskier: bool = False
    example_questions: tuple[str, ...] = ()


TASKS: dict[str, TaskConfig] = {
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
                delivery_cycle_days,
                shipped_after_limit,
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
            "delivery_cycle_days",
        ],
        categorical_features=[
            "customer_key",
            "product_key",
            "seller_key",
            "shipped_after_limit",
        ],
        where_clause="where is_delivered_late is not null",
        positive_class_label="late",
        example_questions=(
            "Don hang nao co nguy co giao tre cao?",
            "Line item nao can uu tien theo doi SLA?",
        ),
    ),
    "low_review": TaskConfig(
        name="low_review",
        problem_type="classification",
        entity_name="order",
        prediction_name="low_review_risk",
        business_goal="Predict whether an order is likely to receive a low review score.",
        source_sql="""
            select
                order_key,
                customer_key,
                order_status,
                total_items,
                distinct_products,
                distinct_sellers,
                total_item_price,
                total_freight_value,
                total_gross_amount,
                total_payment_value,
                max_payment_installments,
                has_installments,
                approval_lead_hours,
                delivery_cycle_days,
                is_delivered_late,
                avg_review_score,
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
            "approval_lead_hours",
            "delivery_cycle_days",
            "avg_review_score",
        ],
        categorical_features=[
            "customer_key",
            "order_status",
            "has_installments",
            "is_delivered_late",
        ],
        where_clause="where is_low_review_order is not null",
        positive_class_label="low_review",
        example_questions=(
            "Don nao co nguy co bi review thap?",
            "Order nao can cham soc khach hang som?",
        ),
    ),
    "customer_value_tier": TaskConfig(
        name="customer_value_tier",
        problem_type="classification",
        entity_name="customer",
        prediction_name="customer_value_segment",
        business_goal="Classify customers into business-friendly value tiers.",
        source_sql="""
            select
                customer_key,
                order_sequence_number,
                cumulative_orders,
                cumulative_revenue,
                cumulative_avg_order_value,
                cumulative_avg_review_score,
                cumulative_late_delivery_ratio,
                days_since_previous_order,
                case
                    when cumulative_revenue >= 1000 then 'high'
                    when cumulative_revenue >= 300 then 'medium'
                    else 'low'
                end as customer_value_segment
            from marts.fact_customer_snapshot
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
        example_questions=(
            "Khach hang nay thuoc nhom gia tri nao?",
            "Tap khach nao la high value customer?",
        ),
    ),
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
                shipped_after_limit,
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
            "shipped_after_limit",
        ],
        where_clause="where delivery_cycle_days is not null",
        lower_is_riskier=False,
        example_questions=(
            "Mat bao nhieu ngay de giao line item nay?",
            "Du kien thoi gian giao hang cua don nay la bao lau?",
        ),
    ),
    "order_value_regression": TaskConfig(
        name="order_value_regression",
        problem_type="regression",
        entity_name="order",
        prediction_name="predicted_order_value",
        business_goal="Estimate order value from order structure and payment behavior.",
        source_sql="""
            select
                order_key,
                customer_key,
                order_status,
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
            "order_status",
            "has_installments",
            "uses_credit_card",
            "uses_voucher",
            "dominant_payment_type",
        ],
        where_clause="where total_payment_value is not null",
        example_questions=(
            "Don hang nay du kien gia tri bao nhieu?",
            "Order nao co kha nang mang lai doanh thu cao?",
        ),
    ),
    "seller_risk_band": TaskConfig(
        name="seller_risk_band",
        problem_type="classification",
        entity_name="seller",
        prediction_name="seller_operational_risk",
        business_goal="Classify sellers into operational risk bands.",
        source_sql="""
            select
                seller_key,
                seller_state,
                total_orders,
                total_items,
                total_gross_item_amount,
                avg_item_amount,
                shipped_after_limit_ratio,
                delivered_late_ratio,
                seller_risk_band
            from marts.dim_sellers
        """,
        target_column="seller_risk_band",
        id_columns=["seller_key"],
        numeric_features=[
            "total_orders",
            "total_items",
            "total_gross_item_amount",
            "avg_item_amount",
            "shipped_after_limit_ratio",
            "delivered_late_ratio",
        ],
        categorical_features=["seller_state"],
        where_clause="where seller_risk_band is not null",
        positive_class_label="high_risk",
        example_questions=(
            "Seller nao dang co rui ro van hanh cao?",
            "Nen uu tien theo doi seller nao?",
        ),
    ),
    "daily_category_revenue_regression": TaskConfig(
        name="daily_category_revenue_regression",
        problem_type="regression",
        entity_name="category_day",
        prediction_name="predicted_daily_category_revenue",
        business_goal="Estimate daily category revenue for demand planning.",
        source_sql="""
            select
                entity_key,
                date_key,
                extract(month from full_date) as calendar_month,
                extract(day from full_date) as calendar_day,
                extract(isodow from full_date) as iso_weekday,
                total_orders,
                total_units,
                total_revenue
            from marts.fact_demand_series
            where entity_type = 'category'
        """,
        target_column="total_revenue",
        id_columns=["entity_key", "date_key"],
        numeric_features=[
            "calendar_month",
            "calendar_day",
            "iso_weekday",
            "total_orders",
            "total_units",
        ],
        categorical_features=["entity_key"],
        where_clause="and total_revenue is not null",
        example_questions=(
            "Doanh thu category ngay mai du kien bao nhieu?",
            "Category nao sap tang truong doanh thu?",
        ),
    ),
}


def get_task(task_name: str) -> TaskConfig:
    if task_name not in TASKS:
        supported = ", ".join(sorted(TASKS))
        raise ValueError(f"Unsupported task '{task_name}'. Supported tasks: {supported}")
    return TASKS[task_name]


def list_tasks() -> list[TaskConfig]:
    return [TASKS[name] for name in sorted(TASKS)]
