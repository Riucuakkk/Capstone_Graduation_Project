# ML Audit Report

## 1. Executive Summary

This audit reviews the machine learning layer implemented in the project under `src/ml/` and the marts used as ML feature stores in `dbt/models/marts/`.

The project currently uses a baseline supervised-learning framework built on scikit-learn pipelines and random forest models. The original implementation provided a useful scaffold, but several tasks had leakage risks because the target was being predicted using same-period or post-outcome features. The codebase has now been revised to reduce leakage and make the tasks closer to real predictive use cases.

### Headline assessment

| Area | Status | Audit note |
| --- | --- | --- |
| ML framework | Good baseline | Centralized task catalog, training, inference, artifact storage |
| Feature engineering | Moderate | Several marts are ML-ready, but still mostly baseline features |
| Leakage control | Improved | High-risk leakage features removed; some tasks reframed to next-period prediction |
| Evaluation design | Improved | Time-based split added when a temporal column exists |
| Productionization | Partial | Model artifacts are saved locally, but prediction facts are still placeholders |
| Explainability | Basic | Risk bands and recommended actions exist, but no feature attribution yet |

## 2. ML Architecture Overview

### Core implementation

| Component | File | Purpose |
| --- | --- | --- |
| Task catalog | `src/ml/tasks.py` | Defines business goal, SQL source, target, features, and inference metadata |
| Training pipeline | `src/ml/pipeline.py` | Loads data, splits train/test, preprocesses features, trains model, computes metrics |
| Train/predict service | `src/ml/service.py` | Orchestrates training, artifact persistence, and batch scoring |
| Artifact store | `src/ml/artifacts.py` | Saves `.joblib` models and `.json` metadata |
| Semantic output | `src/ml/semantic.py` | Converts raw predictions into business-facing risk bands and recommended actions |

### Modeling baseline

| Problem type | Model |
| --- | --- |
| Classification | `RandomForestClassifier` |
| Regression | `RandomForestRegressor` |

### Preprocessing baseline

| Feature type | Transformation |
| --- | --- |
| Numeric | Median imputation |
| Categorical | Most-frequent imputation + one-hot encoding |

### Evaluation metrics

| Problem type | Metrics |
| --- | --- |
| Classification | Accuracy, weighted F1 |
| Regression | RMSE, MAE, R2 |

## 3. Current Trainable Tasks

### 3.1 Task inventory

| Task name | Problem type | Grain | Prediction target | Source |
| --- | --- | --- | --- | --- |
| `late_delivery` | Classification | `order_item` | `is_delivered_late` | `marts.fact_delivery_line_snapshot` |
| `low_review` | Classification | `order` | `is_low_review_order` | `marts.fact_order_snapshot_ml` |
| `customer_value_tier` | Classification | `customer` snapshot | Next-order customer value tier | `marts.fact_customer_snapshot` |
| `delivery_days_regression` | Regression | `order_item` | `delivery_cycle_days` | `marts.fact_delivery_line_snapshot` |
| `order_value_regression` | Regression | `order` | `total_payment_value` | `marts.fact_orders` |
| `seller_risk_band` | Classification | `seller_day` | Next-day seller risk band | `marts.fact_seller_daily` + `marts.dim_sellers` |
| `daily_category_revenue_regression` | Regression | `category_day` | Next-day category revenue | `marts.fact_demand_series` |

### 3.2 Detailed audit by task

| Task | Business purpose | Current target design | Main features after remediation | Audit status |
| --- | --- | --- | --- | --- |
| `late_delivery` | Predict line items likely to be late | Binary target on actual late delivery | Price, freight, dimensions, approval lead time, customer/product/seller IDs | Valid baseline after removing post-outcome fields |
| `low_review` | Predict orders likely to receive low review | Binary target on low review order | Basket structure, payment amount, installment behavior, customer ID | Safer baseline after removing review score and delivery outcome features |
| `customer_value_tier` | Predict who will become higher-value in the next order | Next-order tier derived from `lead(cumulative_revenue)` | Order count, cumulative revenue, AOV, review quality, late ratio, recency | Reframed from descriptive segmentation to forward-looking classification |
| `delivery_days_regression` | Estimate fulfillment duration | Continuous delivery days | Price, freight, dimensions, approval lead, customer/product/seller IDs | Valid baseline after removing shipping-limit leakage |
| `order_value_regression` | Estimate order monetary value | Total payment value | Basket structure, freight, installments, payment-type usage, customer ID | Valid but still baseline; richer pre-purchase features would help |
| `seller_risk_band` | Predict seller operational deterioration | Next-day risk band from `lead(delivered_late_ratio)` | Same-day and lag-1 seller activity and quality ratios | Reframed from static label recreation to next-day risk prediction |
| `daily_category_revenue_regression` | Support demand planning | Next-day revenue from `lead(total_revenue)` | Calendar fields, current volume, lag-1/lag-7 revenue, trailing 7-day average | Reframed from same-day estimation to true short-horizon forecasting |

## 4. Leakage Audit

### 4.1 Issues found in the original baseline

| Task | Original leakage/problem | Why it was risky |
| --- | --- | --- |
| `late_delivery` | Used `delivery_cycle_days` and `shipped_after_limit` | These fields are only fully known after shipping or delivery progress |
| `low_review` | Used `avg_review_score` to predict `is_low_review_order` | The label is directly derived from review score |
| `low_review` | Used fulfillment outcome variables such as late delivery | These are not always available at the intended decision point |
| `customer_value_tier` | Predicted a tier directly derived from current `cumulative_revenue` | This was rule reproduction, not prediction |
| `seller_risk_band` | Predicted a label derived from same-row `delivered_late_ratio` | This was same-period classification, not forward-looking risk |
| `daily_category_revenue_regression` | Used same-day `total_orders` and `total_units` to predict same-day `total_revenue` | This estimated an already-observed quantity instead of forecasting |

### 4.2 Remediation applied

| Task | Remediation |
| --- | --- |
| `late_delivery` | Removed `delivery_cycle_days` and `shipped_after_limit` from feature set |
| `low_review` | Removed `avg_review_score`, `delivery_cycle_days`, `is_delivered_late`, and `order_status` |
| `customer_value_tier` | Switched label to next-order tier via window `lead` |
| `delivery_days_regression` | Removed `shipped_after_limit` from features |
| `order_value_regression` | Removed `order_status` and added temporal split support |
| `seller_risk_band` | Rebuilt task as seller-day next-day classification with lag features |
| `daily_category_revenue_regression` | Rebuilt task as next-day forecasting with lag and rolling features |

## 5. Evaluation Audit

### Current evaluation behavior

The project now uses:

- Time-based holdout when a task defines a temporal column
- Random split only for tasks without a usable time column
- Classification confidence based on the configured positive class when available

### Why this matters

Random splitting can make sequential business data look artificially easy because future patterns may leak into training through same-entity repetition. Time-based splitting better approximates real deployment, especially for customer progression, seller performance, and revenue forecasting tasks.

## 6. Data and Feature Readiness

### Strengths

| Strength | Detail |
| --- | --- |
| ML-ready marts exist | `fact_delivery_line_snapshot`, `fact_order_snapshot_ml`, `fact_customer_snapshot`, `fact_demand_series` |
| Business-friendly grains | Order item, order, customer snapshot, category-day, seller-day |
| Reusable feature sources | Delivery, payment, customer history, seller daily trends |

### Gaps

| Gap | Impact |
| --- | --- |
| No dedicated offline experiment tracking | Hard to compare model versions rigorously |
| No persisted prediction runs in warehouse | BI and GenAI cannot yet consume scored outputs end-to-end |
| No feature importance or SHAP layer | Limited explainability for business users |
| No explicit calibration or threshold tuning | Risk bands may not align well with business alerting needs |
| No backtesting framework for forecasting | Forecast quality is only measured by a single holdout split |

## 7. Deployment and Serving Audit

### Current state

| Capability | Status | Note |
| --- | --- | --- |
| Train from marts | Available | Implemented in `src/ml/train_model.py` |
| Batch predict from marts | Available | Implemented in `src/ml/predict.py` |
| Save model artifact | Available | Local `.joblib` and metadata JSON |
| Save predictions to warehouse | Not implemented | `fact_*_predictions` tables are placeholders only |
| Streamlit ML UI | Not implemented | `streamlit_app/pages/ml_predict.py` and `forecast.py` are empty |

## 8. Reporting-Ready Conclusion

The machine learning layer is a strong baseline prototype and now better aligned with real predictive use cases after leakage remediation. The revised design supports seven baseline tasks spanning order risk, review risk, customer progression, seller operations, fulfillment duration, order value estimation, and short-horizon revenue forecasting.

However, the current implementation should still be described in the thesis/report as a baseline ML framework rather than a production-grade predictive platform. The key remaining improvements are experiment tracking, warehouse write-back for prediction facts, richer historical feature engineering, explainability, and formal backtesting.

## 9. Recommended Next Steps

| Priority | Recommendation | Expected benefit |
| --- | --- | --- |
| High | Materialize prediction outputs into `fact_order_predictions`, `fact_customer_predictions`, and `fact_seller_predictions` | Enables dashboards and GenAI consumption |
| High | Add feature importance / SHAP explanations | Makes predictions easier to trust and defend in reports |
| High | Add forecast backtesting by rolling window | Produces more realistic forecasting evidence |
| Medium | Add hyperparameter search and experiment logging | Improves model quality and reproducibility |
| Medium | Create dedicated churn and repeat-purchase tasks | Aligns implementation with the project strategy document |
| Medium | Build Streamlit pages for ML inference and forecast review | Makes the ML layer demonstrable in the final project |
