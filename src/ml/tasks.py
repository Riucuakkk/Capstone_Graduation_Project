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


# Catalog ML duoc thu gon con 3 bai toan tieu bieu de giam khoi luong mart.
TASKS: dict[str, TaskConfig] = {
    # 1. Demand planning: san pham nao co kha nang ban chay trong 7 ngay toi.
    "product_bestseller": TaskConfig(
        name="product_bestseller",
        problem_type="classification",
        entity_name="product_day",
        prediction_name="next_7d_bestseller_probability",
        business_goal="Predict whether a product will be in the top demand group over the next 7 days.",
        source_sql="""
            select
                ml_sample_key,
                product_key,
                date_key,
                full_date,
                product_category,
                product_name_length,
                product_description_length,
                product_photos_qty,
                product_weight_g,
                product_length_cm,
                product_height_cm,
                product_width_cm,
                weight_band,
                calendar_month,
                calendar_day,
                iso_weekday,
                total_items,
                total_orders,
                total_gross_amount,
                total_freight_value,
                delivered_late_ratio,
                lag_1_total_items,
                lag_1_total_orders,
                lag_1_total_gross_amount,
                trailing_7_sale_day_avg_items,
                trailing_7_sale_day_avg_revenue,
                next_7d_units,
                next_7d_revenue,
                is_bestseller_next_7d
            from marts.fact_ml_product_demand
        """,
        target_column="is_bestseller_next_7d",
        id_columns=["ml_sample_key", "product_key", "date_key"],
        numeric_features=[
            "product_name_length",
            "product_description_length",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
            "calendar_month",
            "calendar_day",
            "iso_weekday",
            "total_items",
            "total_orders",
            "total_gross_amount",
            "total_freight_value",
            "delivered_late_ratio",
            "lag_1_total_items",
            "lag_1_total_orders",
            "lag_1_total_gross_amount",
            "trailing_7_sale_day_avg_items",
            "trailing_7_sale_day_avg_revenue",
        ],
        categorical_features=[
            "product_key",
            "product_category",
            "weight_band",
        ],
        where_clause="where is_bestseller_next_7d is not null",
        time_column="full_date",
        positive_class_label=True,
        example_questions=(
            "San pham nao co kha nang ban chay trong 7 ngay toi?",
            "Nen uu tien ton kho/marketing cho san pham nao?",
        ),
    ),
    # 2. Order operations: don nao co kha nang hoan tat thanh cong.
    "order_success": TaskConfig(
        name="order_success",
        problem_type="classification",
        entity_name="order",
        prediction_name="order_success_probability",
        business_goal="Predict whether an order is likely to become a successful delivered sale.",
        source_sql="""
            select
                ml_sample_key,
                order_key,
                customer_key,
                order_date_key,
                order_date,
                customer_city,
                customer_state,
                total_items,
                distinct_products,
                distinct_sellers,
                total_item_price,
                total_freight_value,
                total_gross_amount,
                payment_transaction_count,
                distinct_payment_type_count,
                total_payment_value,
                max_payment_installments,
                has_installments,
                uses_credit_card,
                uses_voucher,
                dominant_payment_type,
                approval_lead_hours,
                is_successful_order
            from marts.fact_ml_order_success
        """,
        target_column="is_successful_order",
        id_columns=["ml_sample_key", "order_key"],
        numeric_features=[
            "total_items",
            "distinct_products",
            "distinct_sellers",
            "total_item_price",
            "total_freight_value",
            "total_gross_amount",
            "payment_transaction_count",
            "distinct_payment_type_count",
            "total_payment_value",
            "max_payment_installments",
            "approval_lead_hours",
        ],
        categorical_features=[
            "customer_key",
            "customer_city",
            "customer_state",
            "has_installments",
            "uses_credit_card",
            "uses_voucher",
            "dominant_payment_type",
        ],
        where_clause="where is_successful_order is not null",
        time_column="order_date",
        positive_class_label=True,
        example_questions=(
            "Don hang nao co kha nang hoan tat thanh cong?",
            "Don nao can can thiep som de tang ty le giao thanh cong?",
        ),
    ),
    # 3. Regional demand: khu vuc nao de phat sinh mua hang trong 7 ngay toi.
    "geo_high_demand": TaskConfig(
        name="geo_high_demand",
        problem_type="classification",
        entity_name="location_day",
        prediction_name="next_7d_high_demand_area_probability",
        business_goal="Predict whether a customer location will become a high-demand area over the next 7 days.",
        source_sql="""
            select
                ml_sample_key,
                location_key,
                customer_state,
                customer_city,
                date_key,
                full_date,
                calendar_month,
                calendar_day,
                iso_weekday,
                total_orders,
                total_revenue,
                late_delivery_ratio,
                avg_review_score,
                lag_1_total_orders,
                lag_1_total_revenue,
                trailing_7_sale_day_avg_orders,
                trailing_7_sale_day_avg_revenue,
                next_7d_orders,
                next_7d_revenue,
                is_high_demand_area_next_7d
            from marts.fact_ml_geo_demand
        """,
        target_column="is_high_demand_area_next_7d",
        id_columns=["ml_sample_key", "location_key", "date_key"],
        numeric_features=[
            "calendar_month",
            "calendar_day",
            "iso_weekday",
            "total_orders",
            "total_revenue",
            "late_delivery_ratio",
            "avg_review_score",
            "lag_1_total_orders",
            "lag_1_total_revenue",
            "trailing_7_sale_day_avg_orders",
            "trailing_7_sale_day_avg_revenue",
        ],
        categorical_features=[
            "location_key",
            "customer_state",
            "customer_city",
        ],
        where_clause="where is_high_demand_area_next_7d is not null",
        time_column="full_date",
        positive_class_label=True,
        example_questions=(
            "Khu vuc nao co kha nang mua hang cao trong 7 ngay toi?",
            "Nen day campaign hoac chuan bi logistics o dia diem nao?",
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
