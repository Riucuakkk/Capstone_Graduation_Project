
# End-to-End Data Engineering Pipeline for Olist E-commerce Data

## Project Overview
This project builds an end-to-end data engineering pipeline for processing and analyzing the Olist e-commerce dataset.
The system automatically ingests raw data, transforms it using dbt, and prepares structured datasets for analytics using the Data Vault architecture.
The pipeline demonstrates key Data Engineering concepts, including:
- Data ingestion
- Data transformation
- Data warehouse modeling (Data Vault)
- Workflow orchestration
- Containerized deployment

## Business Context
This project uses the Olist Brazilian E-commerce public dataset, built around real e-commerce activity in Brazil and collected by Olist from its marketplace ecosystem.
The dataset covers orders, products, payments, freight, customer geography, and reviews, and is used here to support three practical decision-making scenarios:
- demand planning: identify products that are likely to become bestsellers in the next 7 days so inventory and marketing can be prioritized early
- order operations: identify orders that are at risk of not completing successfully so operations can intervene sooner
- regional planning: identify cities or regions that are likely to show high demand so campaign budget and logistics readiness can be allocated better

## System Architecture
![KienTruc](images/kientruc.png)

The architecture is organized as a layered data platform that moves from raw source ingestion to business-facing analytics and ML consumption:

- Source layer: raw Olist CSV files are ingested into PostgreSQL under the `source` schema as the landing zone for downstream processing.
- Staging layer: dbt standardizes source structures, data types, and naming conventions so later layers work with cleaner, consistent models.
- Raw Vault layer: core business entities such as customers, orders, products, sellers, reviews, and their links are modeled with Data Vault hubs, links, and satellites to preserve history and traceability.
- Business Vault layer: integration logic is added on top of Raw Vault to produce reusable business-aligned structures that are easier to transform into analytical facts and dimensions.
- Datamart layer: dbt builds star-schema style marts and ML-ready fact tables for reporting, KPI tracking, and predictive use cases.
- Orchestration layer: Apache Airflow coordinates ingestion, transformation, data quality checks, mart refresh, and ML jobs in the correct dependency order.
- Serving layer: Superset consumes BI-ready views for dashboards, while the Streamlit app exposes both dashboard navigation and prediction flows for end users.

From an end-to-end flow perspective:

- raw data is loaded into PostgreSQL
- dbt transforms it through staging, vault, and datamart layers
- Airflow schedules and monitors each pipeline stage
- marts and ML outputs are published for BI dashboards and user-facing prediction screens

## Dataset
- Dataset used in this project:
- Olist Brazilian E-commerce Dataset
- Source: Kaggle

## Technology Stack
| Layer               | Tool           |
| ------------------- | -------------- |
| Programming         | Python         |
| Database            | PostgreSQL     |
| Data Transformation | dbt            |
| Orchestration       | Apache Airflow |
| BI Dashboard        | Apache Superset |
| Containerization    | Docker         |
| Data Modeling       | Data Vault 2.0 |
## Running the Project
docker compose up -d

Superset runs at:

```text
http://localhost:8088
```

Default account:

```text
admin / admin
```

Airflow runs at:

```text
http://localhost:8080
```

Default account:

```text
airflow / airflow
```

Connect Superset to the mart warehouse with:

```text
postgresql+psycopg2://airflow:airflow@postgres:5432/ecommerce
```

See `docs/superset_bi_setup.md` for the recommended BI dashboard around the 3 predictive mart use cases.
