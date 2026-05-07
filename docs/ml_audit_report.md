# ML Audit Report

## 1. Executive Summary

The ML layer is now intentionally scoped to 3 representative business problems instead of a broad catalog of experimental tasks. This makes the mart layer lighter, easier to explain in a thesis/report, and easier to demo end to end.

| Area | Status | Audit note |
| --- | --- | --- |
| ML scope | Focused | Reduced to product demand, order success, and geo demand |
| Feature marts | Good baseline | 3 dedicated `fact_ml_*` tables with clear grain and target |
| Leakage control | Improved | Product/geo tasks use next-7-day labels; order task avoids review/delivery-duration outcome fields as features |
| Evaluation design | Good baseline | Time-based split is used when a task has a temporal column |
| Productionization | Partial | Model artifacts are saved locally; warehouse write-back can be added later |

## 2. Current Trainable Tasks

| Task name | Problem type | Grain | Prediction target | Source |
| --- | --- | --- | --- | --- |
| `product_bestseller` | Classification | product-day | Product is in top demand group over next 7 days | `marts.fact_ml_product_demand` |
| `order_success` | Classification | order | Order becomes a successful delivered sale | `marts.fact_ml_order_success` |
| `geo_high_demand` | Classification | city-state-day | Location is in high-demand group over next 7 days | `marts.fact_ml_geo_demand` |

## 3. Business Coverage

| Business question | ML task | Practical action |
| --- | --- | --- |
| San pham nao sap ban chay? | `product_bestseller` | Uu tien ton kho, campaign, seller readiness |
| Don hang nao co kha nang thanh cong? | `order_success` | Uu tien xu ly don tot, can thiep don co score thap |
| Dia diem nao de phat sinh mua hang? | `geo_high_demand` | Chon khu vuc marketing/logistics |

## 4. Mart Readiness

| Mart | Grain | Main feature groups |
| --- | --- | --- |
| `fact_ml_product_demand` | 1 product / ngay co ban | Product attributes, calendar, current demand, lag, rolling demand |
| `fact_ml_order_success` | 1 order | Basket value, payment behavior, installment, customer location |
| `fact_ml_geo_demand` | 1 city-state / ngay co ban | Calendar, regional orders/revenue, review/SLA signal, lag, rolling demand |

## 5. Remaining Risks

| Risk | Note |
| --- | --- |
| Sparse daily rows | Product and geo marts use sale days; a denser calendar grid would improve forecasting rigor |
| Baseline model only | Random forest is fine for demo, but should be compared with boosted trees or time-series backtests later |
| Limited explainability | Feature importance/SHAP should be added before treating predictions as decision automation |
| No prediction write-back | Streamlit/CLI can score, but warehouse prediction facts are not materialized yet |

## 6. Recommended Next Steps

| Priority | Recommendation | Expected benefit |
| --- | --- | --- |
| High | Train and record metrics for the 3 tasks | Produces report-ready evidence |
| High | Add feature importance output to metadata | Makes recommendations explainable |
| Medium | Add dense date-product/date-location grids | Improves next-7-day demand labels |
| Medium | Add prediction write-back tables only after model quality is accepted | Avoids bringing back unnecessary mart weight |

## 7. Conclusion

The revised design is report-friendly and demo-friendly: 3 tasks, 3 ML marts, clear business questions, and no placeholder prediction tables. It should be described as a focused baseline predictive layer, not a full production ML platform.
